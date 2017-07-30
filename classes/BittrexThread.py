import ConfigParser
from Bittrex import Bittrex
import json
import time

class BittrexThread:

    def __init__(self, coin):
        self.config = ConfigParser.ConfigParser()
        self.config.read("config.ini")

        self.exchange = Bittrex(self.config.get('bittrex', 'key'), self.config.get('bittrex', 'secret'))
        self.coin = "BTC-" + coin
        self.plainCoin = coin

        self.quantity = self.config.getfloat('general', 'AMOUNT_BTC_PER_TRADE')

        self.balance = self.exchange.get_balance(coin)
        self.coinBalance = self.balance['result']['Available']

        self.buyCompleted = False

        self.handle()

    def getMarket(self):
        cars = self.exchange.get_ticker(self.coin)
        #for keys, values in cars.items():
        #    print(keys)
        #    print(values)
        return cars['result']['Ask'] + cars['result']['Ask'] * self.config.getfloat('general', 'PERCENT_ADD_ASK')

    def buy(self):
        self.ask = round(self.config.getfloat('general', 'AMOUNT_BTC_PER_TRADE') / self.rate, 8)
        return self.exchange.buy_limit(self.coin, self.ask, self.rate)


    def awaitBuy(self):
        c = 0
        while True:
            balance = self.exchange.get_balance(self.plainCoin)
            if balance['result']['Available'] > self.coinBalance:
                self.buyCompleted = True
                break

            if c > self.config.getint('general', 'TIME_FOR_BUY_CANCEL'):
                break
            c = c + 1
            time.sleep(1)

    def waitForHighestBid(self):

        lastPrice  = 0
        stopLossOrder = 0
        iterator = 0

        while True:
            cPrice = round( float(self.exchange.get_ticker(self.coin)['result']['Ask']), 8)
            tmpStopLossOrder = (1 - self.config.getfloat('general', 'STOP_LOSS_ORDER_PERCENT')) * cPrice
            if tmpStopLossOrder > stopLossOrder:
                if iterator % self.config.getint('general', 'RECALCULATE_STOP_LOSS_SECONDS') == 0:
                    stopLossOrder = tmpStopLossOrder

            if cPrice <= stopLossOrder:
                lastPrice = cPrice
                break
            print("======================================")
            print("=> WAITING FOR SELL SINCE : " + str(iterator) + "s")
            print("=> BUY:" + self.coin + " @ Bittrex")
            print("=> Current Bid Price: ", cPrice)
            print("=> Current Stop Loss: ", stopLossOrder)
            print("======================================")
            lastPrice = cPrice
            iterator = iterator + 1
            time.sleep(self.config.getint('general', 'WAIT_FOR_HIGHEST_BID_SLEEP_SECONDS'))
        return lastPrice

    def handle(self):
        self.rate = self.getMarket()
        self.buyReturn = self.buy()
        self.awaitBuy()
        if self.buyCompleted:
            self.latestPrice = self.waitForHighestBid()
            print("======================================")
            print("TIME TO SELL")
            print( self.exchange.sell_limit(self.coin, round( self.quantity / self.rate, 8 ), self.latestPrice * (1 + self.config.getfloat('general', 'PROFITMARGIN'))) )
