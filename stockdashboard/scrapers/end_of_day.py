import re
import datetime
import time
import itertools
from stockdashboard.scrapers.connection import EstablishConnectionByRequest


class EndOfDayData():
    """
    Web scrape the end of data and current price from yahoo finance 
    """
    
    def __init__(self):
        self.connection = EstablishConnectionByRequest()
    
    def _market_indexes_symbols(self, ticker):
        """
        Check if the ticker passed as argument needs special formatting as per Yahoo Finance
        
        Parameters:
            ticker: The ticker symbol of the company 
            
        Returns:
            output: The formated ticker symbol need for scraping
        """
        
        special_format_tickers = {"S&P 500": "%5EGSPC",
                "DJIA":"%5EDJI",
                "VIX":"%5EVIX",
                "S&P/TSX":"%5EGSPTSE",
                "NASDAQ":"%5EIXIC",
                "RUSSELL 2000":"%5ERUT"}
        
        output = ticker
        if ticker in special_format_tickers.keys():
            output = special_format_tickers[ticker]
        
        return output
    
    def get_eod(self, ticker, end_date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), start_date="01/01/1975"):
        """
        Web scrape the end of data from yahoo finance
        
        Parameters:
            ticker: The ticker symbol of the company 
            start_date: The start date of the end of day data needed   
            end_date: The end date of the end of day data needed     
         
        Returns:
            eod_data_list: The list of tuple of end of data for the stock
        """
    
        self.start = int(time.mktime(datetime.datetime.strptime(start_date, "%d/%m/%Y").timetuple()))
        self.end = int(time.mktime(datetime.datetime.strptime(end_date, "%d/%m/%Y %H:%M:%S").timetuple()))
        self.ticker = self._market_indexes_symbols(ticker.upper())
        self.url = 'https://ca.finance.yahoo.com/quote/{}/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d'.format(self.ticker, self.start, self.end)
        
        try:
            if self.connection.connect(self.url):
                eod_data_list = list()
                body = self.connection.get_body()
                data = str(body.find_all('script'))
                parsed_data_list = re.findall(r'"HistoricalPriceStore":(.*)\]?', data)
                for parsed_data in parsed_data_list:
                    clean_data = re.findall(r'^[^\]]+', parsed_data)
                    for i in clean_data:
                        price_data_list = re.findall(r'"prices":(.*)\]?', i)
                        final_data_list = [x.split(r'},') for x in price_data_list]
                    for final_data in final_data_list[0]:
                        eod_data = re.findall(r'\{"date":(\d+.?\d+),"open":(\d+.?\d+),"high":(\d+.?\d+),"low":(\d+.?\d+),"close":(\d+.?\d+),"volume":(\d+.?\d+),"adjclose":(\d+.?\d+)', final_data)
                        if eod_data:
                            eod_data_list.append(eod_data)
            
                # formating for easier write/update to database 
                eod_data_list = list(itertools.chain.from_iterable(eod_data_list))
                
                return eod_data_list
            return False
        except Exception as e:
            print("YAHOO EOD SCRAPE GET EOD:", e)
            return False
    
    def get_current_price(self, ticker=None):
        """
        Web scrape the current price for the ticker
        
        Parameters:
            ticker: The ticker symbol of the company 
         
        Returns:
            current: A dictionary with the current price and current percentage/dollar change
        """
        
        if ticker is None:
            ticker = self.ticker
        try:
            if self.connection.connect('https://ca.finance.yahoo.com/quote/{}'.format(ticker)):
                body = self.connection.get_body()
                prices = [x.find_all('span',{'data-reactid':'14'}) for x in body.find_all('div',{'data-reactid':'13'})]
                current_price = prices[0][0].text if len(prices) > 0 else None
                
                prices = [x.find_all('span',{'data-reactid':'14'}) for x in body.find_all('div',{'data-reactid':'13'})]
                current_price = prices[0][0].text if len(prices) > 0 else None
                percentages = [x.find_all('span',{'data-reactid':'16'}) for x in body.find_all('div',{'data-reactid':'13'})]
                current_percentage = percentages[0][0].text if len(percentages) > 0 else None
                
                current = {'Current Price':current_price, 'Current Percentage':current_percentage}
                
                return current
            return False
        except Exception as e:
            print("YAHOO EOD SCRAPE GET CURRENT PRICE:", e)
            return False
                    
    def clean_up(self):
        self.connection.close()
        
