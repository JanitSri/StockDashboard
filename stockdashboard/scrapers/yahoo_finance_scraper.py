import os
import re
import datetime
import time
from stockdashboard.scrapers.connection import EstablishConnectionByRequest

class YahooFinanceScraper():
    """
    Web scrape the data from yahoo finance 
    """
    
    def __init__(self):
        self.connection = EstablishConnectionByRequest()
    

    def get_eod_API(self, ticker, *, end_date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), start_date="01/01/1975 00:00:00"):   
        """
        Web scrape the end of data from yahoo finance using the API
        
        Parameters:
            ticker: The ticker symbol of the company 
            start_date: The start date of the end of day data needed   
            end_date: The end date of the end of day data needed     
             
        Returns:
            eod_data: The list of tuple of end of data for the stock
        """
        
        start = int(time.mktime(datetime.datetime.strptime(start_date, 
                                                                "%d/%m/%Y %H:%M:%S").timetuple()))
        end = int(time.mktime(datetime.datetime.strptime(end_date, 
                                                              "%d/%m/%Y %H:%M:%S").timetuple()))
        ticker = ticker.upper()
        url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?formatted=true&crumb=Tib2mBtP9rD&lang=en-CA&region=CA&interval=1d&period1={start}&period2={end}&events=div%7Csplit&corsDomain=ca.finance.yahoo.com'
         
        try:
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['chart']['result'][0]['indicators']['quote'][0]:
                    date = [0 if x is None else x for x in json_data['chart']['result'][0]['timestamp']]
                    open_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['open']]
                    high_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['high']]
                    low_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['low']]
                    close_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['close']]
                    volume = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['volume']]
                    adjclose_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']]
                    eod_data = list(zip(date,open_price,high_price,low_price,close_price,volume,adjclose_price))

                    return eod_data
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_eod_API ERROR: {e}")
            return False
    
    def get_eod_one_min(self, ticker):   
        """
        Web scrape the one minute end of data from yahoo finance
        
        Parameters:
            ticker: The ticker symbol of the company 
            
        Returns:
            all_eod_data: The list of tuple of end of data for the stock
        """
        
        ticker = ticker.upper()
        
        try:
            all_eod_data = list()
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?region=CA&lang=en-CA&includePrePost=false&interval=1m&range=7d&corsDomain=ca.finance.yahoo.com&.tsrc=finance"        
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['chart']['result'][0]['indicators']['quote'][0]:
                    date = [0 if x is None else x for x in json_data['chart']['result'][0]['timestamp']]
                    open_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['open']]
                    high_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['high']]
                    low_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['low']]
                    close_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['close']]
                    volume = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['volume']]
                    eod_data = list(zip(date,open_price,high_price,low_price,close_price,volume))
                    all_eod_data += eod_data 
            
                return all_eod_data
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_eod_one_min ERROR: {e}")
            return False
        
        
    def get_eod_one_hour(self, ticker):   
        """
        Web scrape the one hour end of data from yahoo finance
        
        Parameters:
            ticker: The ticker symbol of the company 
            
        Returns:
            eod_data: The list of tuple of end of data for the stock
        """
        
        ticker = ticker.upper()
        
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?region=CA&lang=en-CA&includePrePost=false&interval=1h&range=730d&corsDomain=ca.finance.yahoo.com&.tsrc=finance"
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['chart']['result'][0]['indicators']['quote'][0]:
                    date = [0 if x is None else x for x in json_data['chart']['result'][0]['timestamp']]
                    open_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['open']]
                    high_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['high']]
                    low_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['low']]
                    close_price = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['close']]
                    volume = [0 if x is None else x for x in json_data['chart']['result'][0]['indicators']['quote'][0]['volume']]
                    eod_data = list(zip(date,open_price,high_price,low_price,close_price,volume))
                    return eod_data
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_eod_one_min ERROR: {e}")
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
            raise Exception('You have to pass a ticker as an argument')
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
            print(f"YahooFinanceScraper.get_current_price ERROR: {e}")
            return False
        
    def get_dividend_history(self, ticker=None):
        """
        Web scrape the historical dividends of a company
        
        Parameters:
            ticker: The ticker symbol of the company 
         
        Returns:
            dividends_history: list of lists of the date and payout of historical
                               dividends
        """
        
        try:
            start_date = int(time.mktime(datetime.datetime.strptime('01/01/1975', 
                                                            "%d/%m/%Y").timetuple()))
            current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            end_date = int(time.mktime(datetime.datetime.strptime(current_date, "%d/%m/%Y %H:%M:%S").timetuple()))
            url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?formatted=true&crumb=Tib2mBtP9rD&lang=en-CA&region=CA&interval=1d&period1={start_date}&period2={end_date}&events=div%7Csplit&corsDomain=ca.finance.yahoo.com'
        
            if ticker is None:
                raise Exception('You have to pass a ticker as an argument')
                
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['chart']['result'][0]['indicators']['quote'][0]:
                    events_exist = json_data['chart']['result'][0].get('events',None)
                    if events_exist:
                        dividends_exist = events_exist.get('dividends',None)
                    
                    if dividends_exist:
                        dividends_history = [[datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d"), dividends_exist[x].get('amount',None)] for x in dividends_exist.keys()]
                        dividends_history = sorted(dividends_history, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))
                        return dividends_history
                    
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_dividend_history ERROR: {e}")
            return False

    def get_company_stats(self, ticker):
        """
        Web scrape the company financial statistics from yahoo finance 
        
        Parameters:
            ticker: The ticker symbol of the company 
    
        Returns:
            stats_output: The dictionary of company stat and value 
        """
    
        # meterics to webscrape for companies 
        METERICS = {'% Held by Insiders': 'heldPercentInsiders',
                     '% Held by Institutions': 'heldPercentInstitutions',
                     '52-Week Change': '52WeekChange',
                     '5-Year Average Dividend Yield': 'fiveYearAvgDividendYield',
                     '10-Day Average Volume': 'averageDailyVolume10Day',
                     '3-Month Average Volume': 'averageDailyVolume3Month',
                     'Beta': 'beta',
                     'Book Value Per Share': 'bookValue',
                     'Current Ratio': 'currentRatio',
                     'Diluted EPS': 'trailingEps',
                     'Dividend Date': 'dividendDate',
                     'EBITDA': 'ebitda',
                     'Enterprise Value': 'enterpriseValue',
                     'Enterprise to EBITDA': 'enterpriseToEbitda',
                     'Enterprise to Revenue': 'enterpriseToRevenue',
                     'ExDividend Date': 'exDividendDate',
                     'Fiscal Year End': 'lastFiscalYearEnd',
                     'Float': 'floatShares',
                     'Forward Annual Dividend Rate': 'dividendRate',
                     'Forward Annual Dividend Yield': 'dividendYield',
                     'Forward EPS': 'forwardEps',
                     'Forward PE': 'forwardPE',
                     'Gross Profit': 'grossProfits',
                     'LastSplit Date': 'lastSplitDate',
                     'Levered Free Cashflow': 'freeCashflow',
                     'Market Capitalization': 'marketCap',
                     'Most Recent Quarter': 'mostRecentQuarter',
                     'Net Income Available to Common': 'netIncomeToCommon',
                     'Operating Cashflow': 'operatingCashflow',
                     'Operating Margin': 'operatingMargins',
                     'PEG Ratio': 'pegRatio',
                     'Payout Ratio': 'payoutRatio',
                     'Price to Book': 'priceToBook',
                     'Price to Sales': 'priceToSalesTrailing12Months',
                     'Profit Margin': 'profitMargins',
                     'Quaterly Revenue Growth': 'revenueGrowth',
                     'Return on Assets': 'returnOnAssets',
                     'Return on Equity': 'returnOnEquity',
                     'Revenue': 'totalRevenue',
                     'Revenue per Share': 'revenuePerShare',
                     'Shares Outstanding': 'sharesOutstanding',
                     'Shares Short': 'sharesShort',
                     'Short% of Float': 'shortPercentOfFloat',
                     'Short% of Shares Outstanding': 'sharesPercentSharesOut',
                     'Short Ratio': 'shortRatio',
                     'Total Cash': 'totalCash',
                     'Total Cash Per Share': 'totalCashPerShare',
                     'Total Debt': 'totalDebt',
                     'Total Debt to Equity': 'debtToEquity',
                     'Trailing Annual Dividend Rate': 'trailingAnnualDividendRate',
                     'Trailing Annual Dividend Yield': 'trailingAnnualDividendYield',
                     'Trailing PE': 'trailingPE'
                  }
        try:
            if self.connection.connect(r'https://ca.finance.yahoo.com/quote/{}/key-statistics'.format(ticker)):
                body = self.connection.get_body()
                data = str(body.find_all('script'))
                values = data.split(r'"QuoteSummaryStore"')
                
                # check if the data needed exits within the scraped data 
                stats_output = dict()
                for key, val in METERICS.items():
                    pattern = '"%s":{(.*?)}' % (val,)
                    found_data = re.findall(pattern, values[1])
                    
                    if found_data:
                        pattern2 = r'"fmt":(.*)'
                        found_stats = re.findall(pattern2, found_data[0])
                    else:
                        found_stats = found_data
                    
                    if found_stats:
                        final_stats_data =  found_stats[0].split(',', 1)[0]
                        final_stats_data = final_stats_data.strip('""')
                        stats_output[key] = final_stats_data
                    else:
                        value_none = 'NAN'
                        stats_output[key] = value_none
                return stats_output
                        
            return False
        except Exception as e:
            print("COMPANY INFO - STATS:", e)
            return False        

    def get_analysts_ratings(self, ticker=None):
        """
        Get current and historical analyst ratings from Yahoo Finance
        
        Parameters:
            ticker: the ticker symbol of the company 
         
        Returns:
            analyst_ratings: list of dictionaries of analyst ratings 
        """
        
        if ticker is None:
            raise Exception('You have to pass a ticker as an argument')
                
        try:
            url = f"https://ca.finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
            if self.connection.connect(url):
                text_response = self.connection.get_raw_data()
                
                if text_response:
                    find_ratings = re.search(r'"upgradeDowngradeHistory":(.*),"pageViews"', text_response).group(1)
                    analyst_ratings = self.connection.get_json_data(find_ratings)
                    return analyst_ratings['history']
            
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_analysts_ratings ERROR: {e}")
            return False
    
    def get_ticker_info(self, ticker):   
        """
        Web scrape the business summary for the ticker
        
        Parameters:
            ticker: The ticker symbol of the company 
            
        Returns:
            all_info: dictionary of business summary 
        """
        
        ticker = ticker.upper()
        
        try:
            all_info = dict()
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?formatted=true&crumb=Tib2mBtP9rD&lang=en-CA&region=CA&modules=summaryProfile%2Cdetails&corsDomain=ca.finance.yahoo.com"
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['quoteSummary']['result'][0]['summaryProfile']:
                    summary = json_data['quoteSummary']['result'][0]['summaryProfile']
                    all_info['Sector'] = summary['sector']
                    all_info['Industry'] = summary['industry']
                    all_info['Full-Time Employees'] = summary['fullTimeEmployees']
                    all_info['Website'] = summary['website']
                    all_info['Business Summary'] = summary['longBusinessSummary']
                    
                return all_info
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_ticker_info ERROR: {e}")
            return False
    
    def get_company_name(self, ticker):
        """
        Web scrape the company full name
        
        Parameters:
            ticker: The ticker symbol of the company 
    
        Returns:
            company_name: dictionary with the ticker and full name 
        """
        ticker = ticker.upper()
        
        try:
            company_name = dict()
            url = f'https://query2.finance.yahoo.com/v1/finance/quoteType/{ticker}?lang=en-CA&region=CA&corsDomain=ca.finance.yahoo.com'
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['quoteType']['result']:
                    result = json_data['quoteType']['result'][0]
                    company_name['ticker'] = result['symbol']
                    company_name['name'] = result['longName']
                
                    return company_name
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_company_name ERROR: {e}")
            return False
    
    def get_company_financials(self, ticker):
        """
        Web scrape the company financial statements 
        
        Parameters:
            ticker: The ticker symbol of the company 
    
        Returns:
            financials_data_output: The dictionary of company's scraped financial information
        """
        ticker = ticker.upper()
        
        try:
            financials_data_output = dict()
            url = f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?formatted=true&crumb=Tib2mBtP9rD&lang=en-CA&region=CA&modules=incomeStatementHistory%2CcashflowStatementHistory%2CbalanceSheetHistory&corsDomain=ca.finance.yahoo.com'
            if self.connection.connect(url):
                json_data = self.connection.get_json_data()
                if json_data['quoteSummary']['result']:
                    fin_data = json_data['quoteSummary']['result'][0]
                    financials_data_output['Cashflow Statement'] = fin_data['cashflowStatementHistory']['cashflowStatements']
                    financials_data_output['Balance Sheet'] = fin_data['balanceSheetHistory']['balanceSheetStatements']
                    financials_data_output['Income Statement'] = fin_data['incomeStatementHistory']['incomeStatementHistory']
                    return financials_data_output
            return False
        except Exception as e:
            print(f"YahooFinanceScraper.get_company_financials ERROR: {e}")
            return False
        
    def clean_up(self):
        self.connection.close()










