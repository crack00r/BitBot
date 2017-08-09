import ConfigParser
from Poloniex import Poloniex
import json
import time


class PoloniexThread:

    def __init__(self, coin):
        self.config = ConfigParser.ConfigParser()
        self.config.read("config.ini")

        self.exchange = Poloniex(self.config.get('poloniex', 'key'), self.config.get('poloniex', 'secret'))
        self.coin = "BTC_" + coin
        self.plainCoin = coin

        self.quantity = self.config.getfloat('general', 'AMOUNT_BTC_PER_TRADE_P')

        self.balance = float( self.exchange.returnBalances()[coin] )
        self.coinBalance = float( self.balance )

        self.buyCompleted = False

        self.handle()

    def getMarket(self):
        cars = self.exchange.returnTicker()
        #for keys, values in cars.items():
        #    print(keys)
        #    print(values)
        return round(float(cars[self.coin]['lowestAsk']) + float(cars[self.coin]['lowestAsk']) * self.config.getfloat('general', 'PERCENT_ADD_ASK'), 8)

    def buy(self):
        self.ask = round(self.config.getfloat('general', 'AMOUNT_BTC_PER_TRADE_P') / self.rate, 8)
        return self.exchange.buy(self.coin, self.rate, self.ask)


    def awaitBuy(self):
        c = 0
        while True:
            balance = float( self.exchange.returnBalances()[self.plainCoin] )
            if balance > self.coinBalance:
                self.buyCompleted = True
                self.coinBalance = balance
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
            cPrice = round( float(self.exchange.returnTicker()[self.coin]['lowestAsk']), 8)
            tmpStopLossOrder = (1 - self.config.getfloat('general', 'STOP_LOSS_ORDER_PERCENT')) * cPrice
            if tmpStopLossOrder > stopLossOrder:
                if iterator % self.config.getint('general', 'RECALCULATE_STOP_LOSS_SECONDS') == 0:
                    stopLossOrder = tmpStopLossOrder

            if cPrice <= stopLossOrder:
                lastPrice = cPrice
                break
            print("======================================")
            print("=> WAITING FOR SELL SINCE : " + str(iterator) + "s")
            print("=> BUY:" + self.coin + " @ Poloniex")
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
            print( self.exchange.sell(self.coin, self.latestPrice * (1 + self.config.getfloat('general', 'PROFITMARGIN')), round( self.coinBalance, 8 )) )
