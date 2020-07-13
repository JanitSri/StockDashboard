from stockdashboard import db, ma, login_manager
import datetime
from collections import OrderedDict
import json
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(32), nullable=False)
  last_name = db.Column(db.String(32), nullable=False)
  email = db.Column(db.String(128), unique=True, nullable=False)
  username = db.Column(db.String(16), unique=True, nullable=False)
  password = db.Column(db.String(64), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

  watchlist_tickers = db.relationship('Security', secondary='Watchlist', backref='user', lazy='dynamic')

  def __repr__(self):
    return f'{self.first_name},{self.last_name},{self.email},{self.username},{self.date_created},{self.last_login}'

db.Table(
        'Watchlist', 
        db.Column('security_ticker', db.String(8), db.ForeignKey('security.ticker'), nullable=False),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
        )


class Security(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), unique=True, nullable=False)
  ticker = db.Column(db.String(8), unique=True, nullable=False)
  date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

  current_news = db.relationship('News', backref='security', lazy='dynamic')
  company_information = db.relationship('Company_Information', backref='security', lazy='dynamic')
  eod_data = db.relationship('Daily_Price', backref='security', lazy='dynamic')
  financials = db.relationship('Financial', backref='security', lazy='dynamic')

  def __repr__(self):
    return f'{self.name},{self.ticker},{self.date_created},{self.last_updated}'


class News(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  header = db.Column(db.String(128), nullable=False)
  link = db.Column(db.String(128), nullable=False)
  source = db.Column(db.String(32), default='unknown')
  date_retrieved = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  security_ticker = db.Column(db.String(8), db.ForeignKey('security.ticker'))

  def __repr__(self):
    return f'{self.header},{self.link},{self.source},{self.date_retrieved},{self.security_ticker}'
  

class Company_Information(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  business_summary = db.Column(db.Text, nullable=True)
  employees = db.Column(db.Integer, nullable=True)
  industry = db.Column(db.String(32), nullable=True)
  sector = db.Column(db.String(32), nullable=True)
  website = db.Column(db.String(64), nullable=True)
  security_ticker = db.Column(db.String(8), db.ForeignKey('security.ticker'), nullable=False)

  def __repr__(self):
    return f'{self.business_summary},{self.employees},{self.industry},{self.sector},{self.website},{self.security_ticker}'


class Daily_Price(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.Date, nullable=False)
  open_price = db.Column(db.Float, nullable=False)
  close_price = db.Column(db.Float, nullable=False)
  adjusted_close_price = db.Column(db.Float, nullable=False)
  low_price = db.Column(db.Float, nullable=False)
  high_price = db.Column(db.Float, nullable=False)
  daily_volume = db.Column(db.Integer, nullable=False)
  security_ticker = db.Column(db.String(8), db.ForeignKey('security.ticker'), nullable=False)

  def __repr__(self):
    return f'{self.date},{self.open_price},{self.close_price},{self.adjusted_close_price},{self.low_price},{self.high_price},{self.daily_volume},{self.security_ticker}'


class Financial(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  cashflow_statement = db.Column(db.Text, nullable=False)
  balance_sheet = db.Column(db.Text, nullable=False)
  income_statement = db.Column(db.Text, nullable=False)
  security_ticker = db.Column(db.String(8), db.ForeignKey('security.ticker'), nullable=False)

  def __repr__(self):
    return f'{json.loads(self.cashflow_statement)},{json.loads(self.balance_sheet)},{json.loads(self.income_statement)},{self.security_ticker}'


class UserSchema(ma.ModelSchema):
  class Meta:
    model = User


class SecuritySchema(ma.ModelSchema):
  class Meta:
    model = Security
  

class NewsSchema(ma.ModelSchema):
  class Meta:
    model = News


class Company_InformationSchema(ma.ModelSchema):
  class Meta:
    model = Company_Information


class Daily_PriceSchema(ma.ModelSchema):
  class Meta:
    model = Daily_Price


class FinancialSchema(ma.ModelSchema):
  class Meta:
    model = Financial