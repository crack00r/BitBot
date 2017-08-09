
import time
import datetime
import random
from bs4 import BeautifulSoup
import pandas as pd
from coinigy import *
import Cryptoping, HandlerThread, BittrexThread, PoloniexThread
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
    # currpair - z.B. BTXBittrex
    currpair=currency+exchange


    if(lastpair!=currpair):
        legitExchange = False
        # Pruefen ob Poloniex oder Bittrex  Wenn ja Transaktion freigeben
        if (exchange == "Poloniex"):
            legitExchange = True
        if (exchange == "Bittrex"):
            legitExchange = True
        
        # Transaktion freigegeben
        if legitExchange:
            if (exchange == "Bittrex"):
                thread.start_new(BittrexThread.BittrexThread, (currency,))
            if (exchange == "Poloniex"):
                thread.start_new(PoloniexThread.PoloniexThread, (currency,))

            lastpair = currpair
    time.sleep(random.randint(1,3))
