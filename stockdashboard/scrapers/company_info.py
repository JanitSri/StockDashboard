import re
from collections import OrderedDict
import codecs
from stockdashboard.scrapers.connection import EstablishConnectionByRequest


class CompanyInformationData():
    """
    Web scrape the company information
    """
    
    def __init__(self):
        self.connection = EstablishConnectionByRequest()
    
    def get_company_name(self, ticker):
        """
        Web scrape the company full name
        
        Parameters:
            ticker: The ticker symbol of the company 
    
        Returns:
            name: The full name of the company 
        """

        try:
            if self.connection.connect(r'https://finance.yahoo.com/quote/{}'.format(ticker)):
                name = [x.text for x in self.connection.get_element('h1')]
                if name:
                    names = name[0].split('-')
                    return [x.strip(' -') for x in names]
                return False
        except Exception as e:
            print("COMPANY INFO - NAME:", e)
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
    
    
    def get_company_general_information(self, ticker):
        """
        Web scrape the company general information from yahoo finance 
        
        Parameters:
            ticker: The ticker symbol of the company 
    
        Returns:
            gen_info_output: The dictionary of company general information
        """
        
        groups = {'Sector':"sector", 'Industry':"industry", 'Business Summary':"longBusinessSummary", 'Website':"website"}
        
        try:
            if self.connection.connect(r'https://ca.finance.yahoo.com/quote/{}'.format(ticker)):
                body = self.connection.get_body()
                data = str(body.find_all('script'))
                values = data.split(r'"summaryProfile"')
                
                gen_info_output = dict()
                if values:
                    for key, val in groups.items():
                        sentence = values[1].split(r'"%s":' % (val, ))
                        matches = re.findall(r'\"(.+?)\"',sentence[1])
                        if matches[0]:
                            if key == 'Website':
                                matches[0] = codecs.decode(matches[0], 'unicode-escape')
                                contains_www = re.findall('http[s]?://www', matches[0])
                                
                                if contains_www:
                                    m = matches[0].split('www.')
                                    gen_info_output[key] = "https://www." + m[1]
                                elif matches[0].startswith('www.'):
                                    m = matches[0].split('www.')
                                    gen_info_output[key] = "https://www." + m[0]
                                else:
                                    gen_info_output[key] = matches[0]
                            else:
                                gen_info_output[key] = matches[0]
                        else:
                            gen_info_output[key] = 'NAN'
                    
                    
                    employee_pattern = '"fullTimeEmployees":("*\w*\d*"*)' 
                    employee_list = re.findall(employee_pattern, values[1])
                    
                    if employee_list:
                        gen_info_output["Full-Time Employees"] = employee_list[0]
                    else:
                        gen_info_output["Full-Time Employees"] = 'NAN' 
                else:
                    gen_info_output['Sector'] = 'NAN'
                    gen_info_output['Industry'] = 'NAN'
                    gen_info_output['Business Summary'] = 'NAN'
                    gen_info_output['Website'] = 'NAN'
                    gen_info_output['Full-Time Employees'] = 'NAN'
                    
                return gen_info_output 
            
            return False
        except Exception as e:
            print("COMPANY INFO - GENERAL INFO:", e)
            return False
    
    
    def get_company_financials(self, ticker):
        """
        Web scrape the company financial statements 
        
        Parameters:
            ticker: The ticker symbol of the company 
    
        Returns:
            company_financials: The dictionary of company's scraped financial information
        """
        
        headers1 = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cookie': 'F=d=5FzQyAM9vIbSw5IUgk854Ejkp.02TQGXvfZtD.U-; AO=u=1; Y=v=1&n=490naqvomigve&l=i0800sbtsh6jg18uu44bx8pcs5xpx9a214pd0bxd/o&p=n2svvca00000000&r=149&intl=ca; GUC=AQEAAQJeAtle2EIeXQR0; ucs=fs=1&lnct=1539063241&bnpt=1551252017&tr=1578059699000; APID=VB862ff5a2-48c5-11e8-8b92-06a80bb5f361; A3=d=AQABBEmNAV4CEI8ppnt_EHspZpTr_QAO7PcFEgEAAQLZAl7YXiXaxyMA_SMAAAcIE-LgWjhu0ZcID6xA6MxAfX0RpAdpsDKEgAkBBwoB8Q&S=AQAAAp6z73YoZyx1i-bCOAiQHKg; A1=d=AQABBEmNAV4CEI8ppnt_EHspZpTr_QAO7PcFEgEAAQLZAl7YXiXaxyMA_SMAAAcIE-LgWjhu0ZcID6xA6MxAfX0RpAdpsDKEgAkBBwoB8Q&S=AQAAAp6z73YoZyx1i-bCOAiQHKg; T=z=zYfDeBdQNLeBCDGEbxjeQYUMzUwMwYzMjQwNDAxMTM2MTEzMT&a=QAE&sk=DAA_gj8o45pHgk&ks=EAA2RvYEmetSjMY4gWI6PZQ_Q--~G&kt=EAA3JNflFDXTUaF9_yLKDl6Xg--~I&ku=FAAscKds_VGS01yibvVTsX_FJZEY2A7_XQbj7qdiVaR9WK_ROJKKMAqWp0.6UsvFAo72_.505AEbHh5Bedpjom1bclQBNdIgpPiQvKg9dbwMUoatC3LxOm0RBZnjtm_hAfJHm9tupZdTqdfTH1U9TZlJuo5A7Jv.UMIuQgpELVF_FE-~A&d=bnMBeWFob28BZwE1TVJUVjI3TUtQVENCNjJIVFZLMlo3RTJYWAFzbAFOREkzTkFFME5UTTNNemMyTmpReE5qWTBOalV5TXpBLQFhAVFBRQFhYwFBSVl2bjVscwFsYXQBb3NGc2RCAWNzAQFhbAFqYW5pdC5zcmkBc2MBZGVza3RvcF93ZWIBZnMBVkdINHVTZGRsVXY5AXp6AUpBeU5lQkE3RQ--&af=JnRzPTE1ODA2NzA5ODUmcHM9bERnTUpYbEhJSDM2bVVieHJlZ3FSdy0t; PH=fn=tI3tBy5.SpB2T8XtKp4-&l=en-CA&i=ca; B=9fkbe71de1ogj&b=4&d=oibaKdBtYFnifBRub6lQ&s=8o&i=rEDozEB9fRGkB2mwMoSA; PRF=t%3DAMZN%252B%255ERUT%252B%255EIXIC%252B%255EDJI%252B%255EGSPTSE%252B%255EVIX%252B%255EGSPC%252BDD; yvapF=%7B%22vl%22%3A237.3430829999999%2C%22rvl%22%3A27.725287%2C%22cc%22%3A3%2C%22rcc%22%3A1%2C%22ac%22%3A1%2C%22al%22%3A14.665147999999999%7D; APIDTS=1584057169; cmp=t=1584057336&j=0; A1S=d=AQABBEmNAV4CEI8ppnt_EHspZpTr_QAO7PcFEgEAAQLZAl7YXiXaxyMA_SMAAAcIE-LgWjhu0ZcID6xA6MxAfX0RpAdpsDKEgAkBBwoB8Q&S=AQAAAp6z73YoZyx1i-bCOAiQHKg',
                    'origin': 'https://ca.finance.yahoo.com',
                    'referer': 'https://ca.finance.yahoo.com/quote/{0}/financials?p={0}'.format(ticker),
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',                    
                   }
        
        all_urls = {
                    'Income Statement': r'https://ca.finance.yahoo.com/quote/{0}/financials?p={0}'.format(ticker),
                    'Balance Sheet': r'https://ca.finance.yahoo.com/quote/{0}/balance-sheet?p={0}'.format(ticker),
                    'Cashflow Statement': r'https://ca.finance.yahoo.com/quote/{0}/cash-flow?p={0}'.format(ticker)
                   }
        
        
        FIN_FORMAT = {
                    "Income Statement": ["Operating Expenses"],
                    "Balance Sheet": ["Assets","Current Assets", "Cash", 
                                      "Non-current assets", "Property, plant and equipment",
                                      "Liabilities and stockholders' equity","Liabilities",
                                      "Current Liabilities","Non-current liabilities",
                                      "Stockholders' Equity"],
                    "Cashflow Statement": ["Cash flows from operating activities", "Cash flows from investing activities",
                                           "Cash flows from financing activities","Free Cash Flow"],
                    }
        
        
        try:
            financials_data_output = dict()
            for key, link in all_urls.items():
                if self.connection.connect(link, headers=headers1):
                    header = self.connection.get_element('div','class','D(tbhg)')
                    dates = [x.find_all('span') for x in header]
                    all_dates = dates[0] if len(dates) > 0 else None
                    
                    rows_of_data = self.connection.get_element('div','data-test','fin-row')
                    columns_of_data = [row.find_all('span') for row in rows_of_data]
                    most_common_length = [len(x) for x in columns_of_data]
                    most_common_length = max(set(most_common_length), key=most_common_length.count)
            
                    financial_dict = OrderedDict()  
                    for row in columns_of_data:                
                        financial_data = list()
                        if(len(row) == most_common_length):
                            row_header = ''        
                            for idx, col in enumerate(row):
                                column_text = col.text.strip()
                                if column_text not in FIN_FORMAT[key]:
                                    if idx == 0: 
                                        row_header = column_text
                                    else:
                                        financial_data.append(column_text)
                                        
                            financial_dict[row_header] = financial_data
                
                    financial_dict.pop('', None)
                
                    if all_dates:
                        final_dates = [x.text for x in all_dates[1:]]
                        financial_dict['header_dates'] = final_dates
                        
                    financials_data_output[key] = financial_dict
        
            return financials_data_output
        except Exception as e:
            print("COMPANY INFO - FINANCIALS:", e)
            return False
    
    def clean_up(self):
        self.connection.close()

