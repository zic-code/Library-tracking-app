from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo,NumberRange

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class LoginForm(UserForm):
    submit = SubmitField('Log In')


class RegistrationForm(UserForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign Up')


class StockFilterForm(FlaskForm):
    sector = SelectField("Select Sector", choices=[], validators=[DataRequired()])
    submit = SubmitField("Filter Stocks")


class InvestmentForm(FlaskForm):
    action = SelectField(
        'Action',
        choices=[('buy', 'Buy'), ('sell', 'Sell')],
        validators=[DataRequired()]
    )
    quantity = DecimalField(
        'Quantity',
        validators=[DataRequired(), NumberRange(min=1)],
        places=2
    )
    submit = SubmitField('Execute Invest')