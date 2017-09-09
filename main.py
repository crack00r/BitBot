
import time
import datetime
import random
from bs4 import BeautifulSoup
import pandas as pd
import HandlerThread, PoloniexThread
import ConfigParser
import thread


config = ConfigParser.ConfigParser()
config.read("config.ini")

firstRun = True

lastpair = ""
currpair = ""

cryptoping = Cryptoping.Cryptoping()

while True:
    currency, exchange = cryptoping.refreshAndGetData()
    if firstRun:
        lastpair=currency+exchange
        firstRun = False
    currpair=currency+exchange


    if(lastpair!=currpair):
        legitExchange = False
        # Pruefen ob Poloniex oder Bittrex  Wenn ja Transaktion freigeben
        if (exchange == "Poloniex"):
            legitExchange = True
       
        # Transaktion freigegeben
        if legitExchange:
            if (exchange == "Poloniex"):
                thread.start_new(PoloniexThread.PoloniexThread, (currency,))

            lastpair = currpair
    time.sleep(random.randint(1,3))
