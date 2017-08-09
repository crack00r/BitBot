import ConfigParser

import time
import datetime

from coinigy import *

class HandlerThread:
    """
    Handles an changing market on bittrex / poloniex
    """

    def __init__(self, currency, exchange, auth_id, exch_id):
        self.currency = currency
        self.exchange = exchange
        self.auth_id = auth_id
        self.exch_id = exch_id
        self.mkt_name = currency + "/BTC"
        self.mkt_id = -1
        self.old_amount_avail = ""
        self.new_amount_avail = ""


        self.config = ConfigParser.ConfigParser()
        self.config.read("config.ini")

        # Setup Coinigy REST API Client
        self.acc = credentials
        self.acc.api = self.config.get('coinigy', 'key')
        self.acc.secret = self.config.get('coinigy', 'secret')
        self.acc.endpoint = self.config.get('coinigy', 'endpoint')
        self.trader = CoinigyREST(self.acc)

        # Run Forrest, run!
        self.handle()

    def printLog(self):
        """
        Prints a simple logline about the currency
        :return: 
        """
        print("=====================================")
        print("=", datetime.datetime.now())
        print("= BUY:\t\t" + self.currency + " @ " + self.exchange)
        print("= Total:\t", self.amount_to_buy)
        print("= Price:\t", self.ask)
        print("= Sell At:\t", self.sellAt)

    def getMarketId(self):
        """
        Reads the market id from coinigy
        :return: 
        """
        markets = self.trader.markets(self.exchange)["data"]
        for m in markets:
            if m["mkt_name"] == self.mkt_name:
                self.mkt_id = m["mkt_id"]
                break

    def refreshBalances(self):
        data = self.trader.refresh_balance(self.auth_id)["data"]
        for d in data:
            if d["balance_curr_code"] == self.currency:
                self.new_amount_avail = d["balance_amount_total"]
                break


    def placeOrder(self):
        """
        Places a new limit-buy order at the given exchange market (Poloniex or Bittrex) and pauses the execution for 5 seconds
        :return: 
        """
        # Order Type ID: 1 = Buy ; 2 = Sell
        # Price Type ID: 3 = Limit; 6 = Stop-Limit; 8 = Limit(Margin); 9 = Stop-Limit(Margin)
        self.order_info = self.trader.add_order(self.auth_id, self.exch_id, self.mkt_id, 1, 3, self.ask, self.amount_to_buy)
        self.order_id = self.order_info["data"]["internal_order_id"]
        print(self.order_info)
        time.sleep(120)

    def awaitBuySuccess(self):
        self.order_cancel_count = 0
        while self.old_amount_avail == self.new_amount_avail:
            data = self.trader.refresh_balance(self.auth_id)["data"]
            for d in data:
                if d["balance_curr_code"] == self.currency:
                    self.new_amount_avail = d["balance_amount_total"]
            self.order_cancel_count = self.order_cancel_count + 1
            if (self.order_cancel_count == self.config.get('general', 'TIME_FOR_BUY_CANCEL')):
                buy_success = False
                self.trader.cancel_order(self.order_id)
                print("=====================================")
                print("=       BUY ORDER NOT EXECUTED      =")
                print("=          SKIPPING TRADE           =")
                print("=====================================")
                break
            time.sleep(180)

    def waitForHighestBid(self):
        """
        Waits with the sell until the bids won't grow anymore
        :return: the latest Bid Price
        """
        lastPrice  = 0
        while True:
            cPriceTemp = self.trader.bids(self.exchange, self.mkt_name)
            cPrice = cPriceTemp.iat[0,0]
            if cPrice < (lastPrice * 0.999):
                break
            print("WAITING FOR SELL:")
            print("= BUY:\t\t\t\t" + self.currency + " @ " + self.exchange)
            print("= Current Bid Price:\t", cPrice)
            lastPrice = cPrice
            time.sleep(10)
        return lastPrice


    def handle(self):
        """
        Handles a new ping on the cryptoping website
        :return: 
        """
        # Buy
        self.ask = self.trader.asks(self.exchange, self.mkt_name).iat[0, 0]
        self.ask = self.ask + (self.ask * self.config.getfloat('general', 'PERCENT_ADD_ASK'))
        self.sellAt = round(self.ask + self.ask * self.config.getfloat('general', 'PROFITMARGIN'), 8)
        self.amount_to_buy = round(self.config.getfloat('general', 'AMOUNT_BTC_PER_TRADE') / self.ask, 8)
        # Print Log
        self.printLog()
        # Get Market Id
        self.getMarketId()
        # Place order
        self.placeOrder()
        # Refresh the balances
        self.refreshBalances()

        # Await Buy success
        self.buy_success = True
        self.awaitBuySuccess()

        # Loop until course doesn't grow anymore
        if self.buy_success == True:
            latestBid = self.waitForHighestBid()
            # Order Type ID: 1 = Buy ; 2 = Sell
            # Price Type ID: 3 = Limit; 6 = Stop-Limit; 8 = Limit(Margin); 9 = Stop-Limit(Margin)
            self.trader.add_order(self.auth_id, self.exch_id, self.mkt_id, 2, 3, 0.995 * latestBid, self.new_amount_avail)
            print("=====================================")
            time.sleep(1)

