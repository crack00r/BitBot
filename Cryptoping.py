import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from coinigy import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class Cryptoping(object):
    """
    Used to read data from Cryptoping.tech
    """

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read("config.ini")
        self.user = self.config.get('cryptoping', 'user')
        self.password = self.config.get('cryptoping', 'password')
        self.isLoggedIn = False
        self.driver = webdriver.Chrome()

        # Setup Coinigy REST API Client
        self.acc = credentials
        self.acc.api = self.config.get('coinigy', 'key')
        self.acc.secret = self.config.get('coinigy', 'secret')
        self.acc.endpoint = self.config.get('coinigy', 'endpoint')
        self.trader = CoinigyREST(self.acc)

        self.loginUser()

    def loginUser(self):
        self.driver.get("https://cryptoping.tech/users/sign_in")

        elem = self.driver.find_element_by_id('user_email')
        elem.click()

        for letter in self.user:
            elem.send_keys(letter)

        elem = self.driver.find_element_by_id('user_password')
        elem.click()

        for letter in self.password:
            elem.send_keys(letter)

        elem = self.driver.find_element_by_name("commit")
        elem.click()

    def getCurrencyAndExchange(self, html):
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", {"class":"results-table full-width"})
        tbody = table.find_all('tbody')
        tr = table.find_all('tr')[1]
        tds = tr.find_all('td')
        currency = tds[0].text.strip().split('\n')[0]
        exchange = tds[-1].text.strip()
        return currency, exchange

    def refreshAndGetData(self):
        self.driver.get("https://cryptoping.tech/backend")
        html = self.driver.page_source
        return self.getCurrencyAndExchange(html)
