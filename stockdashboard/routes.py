from flask import render_template, url_for, request, flash, redirect, jsonify, make_response, send_file, session
import concurrent.futures
import datetime
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd

from stockdashboard import app, cache, bcrypt, login_manager
from stockdashboard.utils import search_bar_data
from stockdashboard.plots.plots import make_plot
from stockdashboard.signals import technical_signal_calculations
from stockdashboard.controller import get_all_data, get_tech_ind, add_user, user_exists, get_latest_ticker_price, get_all_news, get_ticker_news, get_user_watchlist, add_user_watchlist, delete_user_watchlist, update_user_login
from stockdashboard.forms import RegistrationForm, LoginForm

search_bar_options = cache.get('search_bar_options')
if not search_bar_options:
  search_bar_options = search_bar_data()
  cache.set('search_bar_options', search_bar_options)


def cache_data(ticker="TSLA"):
  # handle various entry points 
  print("GETTING DATA")
  return get_all_data(ticker)  


@app.template_filter('datetimeformat')
def datetimeformat(value, formatted='%A, %B %d, %Y'):
  if isinstance(value, str):
    value = datetime.datetime.strptime(value, "%Y-%m-%d").date()

  format_time = value.strftime(formatted)
  return format_time


@app.route('/overview', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
  HOME_TITLE = 'Stock Dashboard'

  current_cache_ticker = cache.get('comp_ticker')

  if not current_cache_ticker:
    current_cache_ticker = 'TSLA'
    
  user_ticker = request.values.get('search-bar-ticker', default=current_cache_ticker)

  print('CURRENT TICKER',user_ticker)
  get_data = True
  if user_ticker != cache.get('comp_ticker'):
    get_data = cache_data(user_ticker)
    if get_data:
      current_cache_ticker = cache.get('comp_ticker')
      get_tech_ind()
    else:
      flash(f"'{user_ticker}'' is an INVALID ticker symbol", 'danger')
  
  if get_data:
    get_ticker_news(current_cache_ticker)

  bar = make_plot(cache.get('comp_eod'))
  cache.set('eod_data_plot',bar)
  
  return render_template('overview.html', title=HOME_TITLE, comp_name=cache.get('comp_name'),comp_ticker=current_cache_ticker, search_data=search_bar_options, plot=cache.get('eod_data_plot'), gen_info=cache.get('comp_gen_info'), curr_ticker_news=cache.get('comp_news'))


@app.route('/watchlist')
@login_required
def watchlist():
  WATCHLIST_TITLE = 'Your Watchlist'

  user_watchlist = get_user_watchlist(current_user.email)
  
  return render_template('watchlist.html', title=WATCHLIST_TITLE, search_data=search_bar_options, user_watchlist=user_watchlist)


@app.route('/marketnews')
def marketnews():
  NEWS_TITLE = 'Current Market News'

  news_data = get_all_news()

  return render_template('marketnews.html', title=NEWS_TITLE, search_data=search_bar_options, google_news_data=news_data['google'],financial_post_news_data=news_data['financial_post'], marketwatch_news_data=news_data['marketwatch'], business_insider_news_data=news_data['business_insider'])


@app.route('/chartdata')
def chartdata():
  CHART_DATA_TITLE = 'Chart Data'

  if not cache.get('comp_eod'):
    cache_data()

  return render_template('chartdata.html', title=CHART_DATA_TITLE, search_data=search_bar_options, comp_name=cache.get('comp_name'),comp_ticker=cache.get('comp_ticker'), eod_data=cache.get('comp_eod'))


@app.route('/technicalindicators')
def techindicators():
  TECHNICAL_INDICATORS_TITLE = 'Technical Indicators'

  if not cache.get('tech_ind'):
    cache_data()
    get_tech_ind()
  
  return render_template('technicalindicators.html', title=TECHNICAL_INDICATORS_TITLE, search_data=search_bar_options, comp_name=cache.get('comp_name'), comp_ticker=cache.get('comp_ticker'), tech_ind_data=cache.get('tech_ind'))


@app.route('/statistics')
def stats():
  STATISTICS_TITLE = 'Statistics'

  if not cache.get('comp_stats'):
    cache_data()
  
  return render_template('statistics.html', title=STATISTICS_TITLE, search_data=search_bar_options, comp_name=cache.get('comp_name'), comp_ticker=cache.get('comp_ticker'), stats_data=cache.get('comp_stats'))


@app.route('/financials')
def financials():
  FINANCIALS_TITLE = 'Financials'
  
  if not cache.get('comp_fins'):
    cache_data()
  
  return render_template('financials.html', title=FINANCIALS_TITLE, search_data=search_bar_options, comp_name=cache.get('comp_name'), comp_ticker=cache.get('comp_ticker'), fin_data=cache.get('comp_fins'))


@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))

  LOGIN_TITLE = 'Login To Your Account'
  form = LoginForm()
  if form.validate_on_submit():
    user = user_exists(form.email.data)
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, form.remember.data)
      update_user_login(user)
      next_page = request.args.get('next')[1:] if request.args.get('next') and request.args.get('next').startswith('/') else request.args.get('next')

      if next_page == 'get_daily_price_csv':
        return render_template('chartdata.html', title='Chart Data', search_data=search_bar_options, comp_name=cache.get('comp_name'), comp_ticker=cache.get('comp_ticker'), eod_data=cache.get('comp_eod'))

      if next_page == 'get_tech_ind_csv':
        return render_template('technicalindicators.html', title='Technical Indicators', search_data=search_bar_options, comp_name=cache.get('comp_name'), comp_ticker=cache.get('comp_ticker'), tech_ind_data=cache.get('tech_ind'))

      return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))
    else: 
      flash(f'Login unsuccessful. Please try again', 'danger')

  return render_template('login.html', title=LOGIN_TITLE, search_data=search_bar_options, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('home'))

  REGISTER_TITLE = 'Sign Up'
  form = RegistrationForm()

  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
    add_user(form.first_name.data, form.last_name.data, form.email.data, hashed_password)
    flash(f'Account successfully registered for {form.first_name.data} {form.last_name.data}.', 'success')
    return redirect(url_for('home')) 

  return render_template('register.html', title=REGISTER_TITLE, search_data=search_bar_options, form=form)


@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('home')) 


@app.route('/get_price', methods=['POST'])
def get_price():
  ticker = request.get_json(force=True)
  result = get_latest_ticker_price(ticker['ticker_name'])
  print("SENDING DATA FOR",ticker['ticker_name'],result)
  
  res = make_response(jsonify({'new_price':result['Current Price'], 'new_price_diff':result['Current Percentage']}), 200)
  return res


@app.route('/get_daily_price_csv')
@login_required
def get_daily_price_csv():
  print("DOWNLOADING DAILY PRICE CSV")
  df = pd.DataFrame(cache.get('comp_eod'), columns =['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose'])
  df.to_csv(r'outputs\daily_price.csv')
  return send_file(r'..\outputs\daily_price.csv',
                     mimetype='text/csv',
                     attachment_filename='daily_price.csv',
                     as_attachment=True)


@app.route('/get_tech_ind_csv')
@login_required
def get_tech_ind_csv():
  print("DOWNLOADING TECHNICAL INDICATORS CSV")
  df =  pd.DataFrame.from_dict(cache.get('tech_ind'), orient='index')
  df.to_csv(r'outputs\technical_indicators.csv')
  return send_file(r'..\outputs\technical_indicators.csv',
                     mimetype='text/csv',
                     attachment_filename='technical_indicators.csv',
                     as_attachment=True)


@app.errorhandler(404)
def not_found(e):
  return render_template('error.html')


@app.route('/parse_date', methods=['POST'])
def parse_date():
  dates_to_parse = request.get_json(force=True)  
  
  if dates_to_parse['start_date'] == "reset_dates":
    return render_template('eoddata.html', eod_data=cache.get('comp_eod'))
  
  start_date = datetime.datetime.strptime(dates_to_parse['start_date'][:10], "%Y-%m-%d").date() 
  end_date = datetime.datetime.strptime(dates_to_parse['end_date'][:10], "%Y-%m-%d").date()

  df = pd.DataFrame(cache.get('comp_eod'), columns =['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose'])
  
  temp_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
  output = temp_data.values.tolist()

  return render_template('eoddata.html', eod_data=output)


@app.route('/parse_date_tech_ind', methods=['POST'])
def parse_date_tech_ind():
  dates_to_parse = request.get_json(force=True)  
  
  if dates_to_parse['start_date'] == "reset_dates":
    return render_template('techind.html', tech_ind_data=cache.get('tech_ind'))
  
  start_date = datetime.datetime.strptime(dates_to_parse['start_date'][:10], "%Y-%m-%d").date().strftime("%Y-%m-%d")
  end_date = datetime.datetime.strptime(dates_to_parse['end_date'][:10], "%Y-%m-%d").date().strftime("%Y-%m-%d")
  
  df = pd.DataFrame.from_dict(cache.get('tech_ind'), orient='index')
  temp_data = df.loc[start_date:end_date]
  output = temp_data.to_dict('index')

  return render_template('techind.html', tech_ind_data=output)


@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
  request_symbol = request.get_json(force=True)
  result = add_user_watchlist(current_user.email,request_symbol['symbol'])
  print('SENDING ADD WATCHLIST DATA', request_symbol['symbol'])

  if not result:
    print("NO DATA")
    return "False"
  
  user_watchlist = get_user_watchlist(current_user.email)
  return render_template('watchlistdata.html', user_watchlist=user_watchlist)


@app.route('/delete_from_watchlist', methods=['POST'])
def delete_from_watchlist():
  request_symbol = request.get_json(force=True)
  result = delete_user_watchlist(current_user.email, request_symbol['symbol'])
  print('SENDING DELETE WATCHLIST DATA', request_symbol['symbol'])
  return jsonify({'message':"TRUE"})


