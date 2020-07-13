from stockdashboard import db, cache
from stockdashboard.models import User, Security, News, Company_Information, Daily_Price, Financial
from stockdashboard.scrapers import financial_news, yahoo_finance_scraper
from stockdashboard.signals.technical_signal_calculations import get_techical_indicators

import datetime
import json
import numpy as np 
import pandas as pd 
import concurrent.futures

# Instantiate the scraping classes  
yahoo = yahoo_finance_scraper.YahooFinanceScraper()
fin_news_data = financial_news.FinancialNewsData()

def get_all_data(ticker='tsla'):
  """
  Gets the data for the specified ticker, either from the database or by webscrape 
  
  Parameters:
      ticker: the ticker to get the data for  
        
  Returns:
      Boolean: True, if the data exists or else false
  """

  ticker = ticker.upper()
  end = _get_end_date()
  ticker_in_DB = ticker_exists(ticker)
  if ticker_in_DB: # check if the ticker exists in the DB
    _update_eod_DB(ticker, end, ticker_in_DB)
  else:
    added_data = _add_new_data(ticker, end)

    if not added_data:
      return added_data
    
  db.session.commit()
  
  cach_ticker = Security.query.filter(Security.ticker == ticker).first()
  cach_ticker.last_updated = datetime.datetime.utcnow()

  ticker_stats = get_stats_data(ticker)
  cach_ticker_eod_data = clean_eod_data(cach_ticker.eod_data.all())
  cach_ticker_fiancials = clean_financials(cach_ticker.financials.all()[-1])
  cach_ticker_comp_info = clean_company_information(cach_ticker.company_information.all()[-1])

  cache.set('comp_eod',cach_ticker_eod_data)
  cache.set('comp_fins',cach_ticker_fiancials)
  cache.set('comp_gen_info',cach_ticker_comp_info)
  cache.set('comp_stats',ticker_stats)
  cache.set('comp_name',cach_ticker.name)
  cache.set('comp_ticker',cach_ticker.ticker)
  

  if not cache.get('sp500_eod'):
    print('GETTING SP500 DATA')
    _add_SP500_data("^GSPC", end)
    
  return True


def _get_end_date():
  """
  Get the last date of the data stored for a ticker, if the market is open get the previous day data 

  Returns:
    end: the end date to get the data for  
  """
  
  today = datetime.datetime.now()
  day_range = today.weekday() in range(1, 6) # check if between Tuesday - Saturday
  
  if not day_range:
      day = today.replace(minute=0, hour=3, second=0, microsecond=0)
      days_away_from_saturday = abs(((day.weekday() + 1) % 7) - 6)
      end = day - datetime.timedelta(weeks=1) + datetime.timedelta(days=days_away_from_saturday)
  else:
      end = (datetime.datetime.combine(today, datetime.datetime.min.time()) + datetime.timedelta(hours=7))
  
  return end.replace(hour=7, minute=0, second=0, microsecond=0).strftime("%d/%m/%Y %H:%M:%S")


def get_stats_data(ticker):
  """
  Get stats data for the ticker 
  
  Parameters:
      ticker: the ticker to get the data for  
        
  Returns:
      ticker_stats: the stats data for the ticker  
  """
  
  ticker = ticker.upper()
  
  if yahoo.get_company_stats(ticker):
      return yahoo.get_company_stats(ticker)
  
  return False


def get_latest_ticker_price(ticker):
  """
  Get the latest ticker price for automatic update 

  Parameters:
    ticker: the ticker symbol of the stock 
  
  Returns:
    price: returns the current price 
  """

  return yahoo.get_current_price(ticker)

  
def ticker_exists(ticker):
  """
  Check if the ticker already exists in the DB

  Parameters:
    ticker: the ticker symbol of the stock 
  
  Returns:
    ticker: the ticker DB object 
  """

  return Security.query.filter(Security.ticker == ticker).first()


def _update_eod_DB(ticker, end, ticker_DB):
  """
  Update the eod_data in the DB
  
  Parameters:
      ticker: the ticker to insert the data for 
      eod_data: the eod data to be inserted into the DB
      ticker_DB: the DB object for the ticker 
  """

  ticker_data = ticker_DB.eod_data.all()[-1]
  recent_date = ticker_data.date
  recent_end = datetime.datetime.strptime(_get_end_date(),'%d/%m/%Y %H:%M:%S')
  print("CURRENT DATE", recent_end.date())
  print("RECENT EOD DATA DATE IN DB", recent_date)
  
  if recent_end.weekday() == 0:
    recent_end = recent_end + datetime.timedelta(days=-3)
  elif recent_end.weekday() == 6:
    recent_end = recent_end + datetime.timedelta(days=-2)
  else:
    recent_end = recent_end + datetime.timedelta(days=-1)

  if (recent_end).date() != recent_date: # check the latest date of the eod data 
    print('DB UPDATING, GETTING MISSING ' + ticker + ' EOD DATA')
    recent_date = datetime.datetime.strptime(recent_date.strftime('%d/%m/%Y %H:%M:%S'), '%d/%m/%Y %H:%M:%S')
    next_day = (recent_date.replace(hour=9, minute=30, second=0) + datetime.timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S")
    
    recent_eod = yahoo.get_eod_API(ticker, start_date=next_day, end_date=end)
    if recent_eod:
      recent_eod = [x for x in recent_eod if x and datetime.datetime.fromtimestamp(int(x[0])).hour in range(9,10)]
      _add_daily_price_DB(recent_eod, ticker)


def _add_new_data(ticker, end):
  """
  Adds new ticker data to the DB
  
  Parameters:
      ticker: the ticker to get the data for  
      end: the end date to get the ticker data 
        
  Returns:
      Boolean: True, if the data exists or else false
  """

  print("ADDING NEW DATA", ticker)
  
  eod_data_curr = yahoo.get_eod_API(ticker,end_date=_get_end_date())

  with concurrent.futures.ThreadPoolExecutor() as executor:
      results = [executor.submit(funcs, ticker) 
                 for funcs in [yahoo.get_ticker_info, 
                               yahoo.get_company_name,yahoo.get_company_financials]]
  
  ticker_eod = eod_data_curr
  ticker_gen_info = results[0].result()
  ticker_name = results[1].result()
  ticker_fins = results[2].result()
  if not ticker_eod: # check if the ticker has any eod data 
    print("EOD DATA DOES NOT EXISTS",ticker)
    return False

  print("EOD DATA EXISTS",ticker)

  # add the securty name and ticker to db
  _add_security_DB(ticker_name['name'], ticker)

  # add the end of day data to db
  _add_daily_price_DB(ticker_eod, ticker)

  # add the company general information data to db
  _add_comp_info_DB(ticker_gen_info, ticker)

  # add the company financials data to db
  _add_financial_DB(ticker_fins, ticker)

  return True


def _add_daily_price_DB(eod_data, ticker):
  """
  Add the end of day data to the db
  
  Parameters:
      ticker: the ticker to insert the data for 
      eod_data: the eod data to be inserted into the DB
  """

  for eod in eod_data:
        db.session.add(Daily_Price(date=datetime.datetime.utcfromtimestamp(int(eod[0])),open_price=float(eod[1]),close_price=float(eod[4]),adjusted_close_price=float(eod[6]),low_price=float(eod[3]),high_price=float(eod[2]), daily_volume=float(eod[5]),security_ticker=ticker))


def _add_security_DB(ticker_name, ticker):
  """
  Add the security name and ticker to db 
  
  Parameters:
      ticker: the ticker to insert the data for 
      ticker_name: the ticker name to be inserted into the DB
  """
    
  db.session.add(Security(name=ticker_name, ticker=ticker))


def _add_comp_info_DB(ticker_gen_info, ticker):
  """
  Add the general company information data to the db
  
  Parameters:
      ticker: the ticker to insert the data for 
      ticker_gen_info: the general company information data to be inserted into the DB
  """

  db.session.add(Company_Information(business_summary=ticker_gen_info['Business Summary'],employees=ticker_gen_info['Full-Time Employees'],industry=ticker_gen_info['Industry'],sector=ticker_gen_info['Sector'],website=ticker_gen_info['Website'],security_ticker=ticker))


def _add_financial_DB(ticker_fins, ticker):
  """
  Add the company financial data to the db
  
  Parameters:
      ticker: the ticker to insert the data for 
      ticker_fins: the company financial data to be inserted into the DB
  """

  db.session.add(Financial(cashflow_statement=json.dumps(ticker_fins['Cashflow Statement']),balance_sheet=json.dumps(ticker_fins['Balance Sheet']),income_statement=json.dumps(ticker_fins['Income Statement']),security_ticker=ticker))


def _add_news_DB(header, link, ticker, source='google'):
  """
  Add the company or market news data to the db
  
  Parameters:
      ticker: the ticker to insert the data for 
      header: the news header for the article 
      link: the link for the news article 
      source: the source of the news article 
  """

  db.session.add(News(header=header,link=link,source=source,security_ticker=ticker))


def clean_eod_data(db_eod_data):
  """
  Clean the end of day data 
  
  Parameters:
      db_eod_data: the eod data to be cleaned 
  """

  output = list()
  for data in db_eod_data:
    output.append([data.date, data.open_price, data.high_price, data.low_price, data.close_price, data.daily_volume, data.adjusted_close_price])
  
  return output


def clean_financials(db_financials):
  """
  Clean the ticker financial data 
  
  Parameters:
      db_financials: the ticker financial data to be cleaned 
  """

  output = dict()
  output['cashflow'] = json.loads(db_financials.cashflow_statement)
  output['income'] = json.loads(db_financials.income_statement)
  output['balance'] = json.loads(db_financials.balance_sheet)

  return output


def clean_company_information(db_comp_info):
  """
  Clean the company general information data 
  
  Parameters:
      db_comp_info: the company general information data to be cleaned 
  """

  output = dict()
  output['business_summary'] = db_comp_info.business_summary
  output['employees'] = db_comp_info.employees
  output['industry'] = db_comp_info.industry
  output['sector'] = db_comp_info.sector
  output['website'] = db_comp_info.website

  return output


def _add_SP500_data(ticker, end_date):
  """
  Adds sp500 or other index data to the DB 
  
  Parameters:
      ticker: the ticker to get the data for  
      end: the end date to get the ticker data 
  """

  ticker_in_DB = ticker_exists(ticker)
  if ticker_in_DB:
    _update_eod_DB(ticker, end_date, ticker_in_DB)
  else:
    _add_security_DB("Standard&Poor 500", ticker)
    ticker_eod = yahoo.get_eod_API(ticker, end_date=end_date)
    
    _add_daily_price_DB(ticker_eod, ticker)
    
  db.session.commit()
  cach_ticker = Security.query.filter(Security.ticker == ticker).first()
  cach_ticker.last_updated = datetime.datetime.utcnow()
  cache.set('sp500_eod', clean_eod_data(cach_ticker.eod_data.all()))


def get_ticker_news(ticker):
  """
  Get the news for the ticker 

  Parameters:
    ticker: the ticker symbol of the stock 
  """

  # add the current company news data to db 
  cach_ticker = Security.query.filter(Security.ticker == ticker).first()
  cach_ticker.last_updated = datetime.datetime.utcnow()

  if cach_ticker:
    print("GETTING NEWS FOR", ticker)
    ticker_news = fin_news_data.get_google_news(ticker)
    for header_data, link_data in ticker_news.items():
      if not News.query.filter(News.header == header_data).first():
        # print(ticker + ' NEWS: ADDING', header_data)
        _add_news_DB(header_data, link_data, ticker, 'google')

    db.session.commit() 

  cach_ticker_news = clean_news(cach_ticker.current_news.all())[::-1]
  cache.set('comp_news', cach_ticker_news) 


def clean_news(db_news):
  """
  Clean the ticker or market news data 
  
  Parameters:
      db_news: the news data to be cleaned 
  """

  output = list()
  for data in db_news:
    output.append([data.header, data.link, data.source])
  
  return output


def get_all_news(): # done
  """
  Get the news for the entire market  
  """

  print('GETTING ALL NEWS')
  all_news_funcs = [fin_news_data.get_financial_post_news,fin_news_data.get_market_news,fin_news_data.get_marketwatch_news, fin_news_data.get_business_insider_news]

  with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(func) for func in all_news_funcs]

  all_news_dict = {
    "financial_post":results[0].result(),
    "google":results[1].result(),
    "marketwatch":results[2].result(),
    "business_insider":results[3].result(),
  }

  # current_news_in_DB = clean_news(News.query.all())
  # existing_headers = [x[0] for x in current_news_in_DB] if len(current_news_in_DB) > 0 else []  
  for news_source, news_results in all_news_dict.items():
    for header, link in news_results.items():
      if not News.query.filter(News.header == header).first():
        # print('ALL NEWS: ADDING ', header)
        _add_news_DB(header, link, None, news_source)

  db.session.commit()
  updated_news_in_DB = clean_news(News.query.all())[::-1]
  
  result_dict = {
    "financial_post": list(),
    "google": list(),
    "marketwatch": list(),
    "business_insider": list(),
  }
  
  for news in updated_news_in_DB:
    result_dict[news[2]].append(news)
  
  return result_dict


def get_tech_ind():
  """
  Calculate the technical indicators and cache the data 
  """
  cache.set('tech_ind',get_techical_indicators(cache.get('comp_eod'), cache.get('sp500_eod')))


def user_exists(email):
  """
  Check if user exists using email 

  Parameters:
    email: User's email address
  
  Returns:
    user: user DB object 
  """

  return User.query.filter_by(email=email).first()

def get_user_watchlist(user_email):
  """
  Get the watchlist of the user

  Parameters:
    user_email: the email of the user 
  """

  user = user_exists(user_email)
  if user:
    all_tickers = user.watchlist_tickers.all()
    output_ticker_data = list() 
    for ticker in all_tickers:
      ticker_name = ticker.ticker
      comp_name = ticker.name
      sector = ticker.company_information[0].sector
      industry = ticker.company_information[0].industry
      previous_close = ticker.eod_data[-1].close_price 
      previous_volume = ticker.eod_data[-1].daily_volume 
      output_ticker_data.append([ticker_name,comp_name,sector,industry,previous_close,previous_volume])
      
  return output_ticker_data


def add_user_watchlist(user_email, ticker):
  """
  Add ticker to the watchlist of the user 

  Parameters:
    user_email: the email of the user 
    ticker: ticker symbol to add to watchlist 
  """

  ticker_data = ticker_exists(ticker)
  end = _get_end_date()
  if not ticker_data:
    added_data = _add_new_data(ticker, end)
    if not added_data:
      return added_data
    
    db.session.commit()
    
  ticker_data = ticker_exists(ticker)
  ticker_list = ticker_data.user

  if user_exists(user_email) not in ticker_list:
    print(ticker, 'NOT IN WATCHLIST')
    ticker_data.user.append(user_exists(user_email))
  
  db.session.commit()

  return True


def delete_user_watchlist(user_email, ticker):
  """
  Remove ticker from the watchlist of the user 

  Parameters:
    user_email: the email of the user 
    ticker: ticker symbol to add to watchlist 
  """

  ticker_data = ticker_exists(ticker)
  if ticker_data:
    print(ticker, "REMOVING FROM WATCHLIST")
    ticker_data.user.remove(user_exists(user_email))
    db.session.commit()
    return True 
  
  return False


def add_user(first_name, last_name, email, password):
  """
  Add the data for the user from the registration page 

  Parameters:
    first_name: User's first name
    last_name: User's last name 
    email: User's email address
    password: User's password
  """
  db.session.add(User(first_name=first_name,last_name=last_name,email=email,username=email,password=password))
  db.session.commit()
  return True 


def update_user_login(user):
  """
  Update the last login of the user

  Parameters:
    user: the DB object of the user
  """

  user.last_login = datetime.datetime.utcnow()
  db.session.commit()
  return True 