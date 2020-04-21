from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField, BooleanField  
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError

from stockdashboard.models import User

class RegistrationForm(FlaskForm):
  first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=30)])
  last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=30)])
  email = StringField('Email Address', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), Regexp(r'[A-Za-z0-9@#$%^&+=]{8,}', message='Password must be at least 8 characters and contain uppercase, lowercase, numbers, and special characters (@#$%^&+=).')])
  confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password',message='Passwords do not match.')])
  submit = SubmitField('Sign Up')

  def validate_email(self, email):
    user_exists = User.query.filter(User.email == email.data).first() or User.query.filter(User.username == email.data).first()
    if user_exists:
      raise ValidationError('Email is taken, please try again.')

class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')

