
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField, IntegerField, TimeField, SelectField
from wtforms.validators import Required, EqualTo, DataRequired, Length
from flask_admin.form import widgets
from datetime import datetime




class LoginForm(FlaskForm):
    
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('admin1')])

    username = StringField('Username', validators=[DataRequired(), EqualTo('admin')])

    submit_login = SubmitField('Login')

class InputsForm(FlaskForm):

    quantity = FloatField('Quantity', validators=[Required()])

    pips_buy = FloatField('Pips Buy', validators=[Required()])

    pips_sell = FloatField('Pips Sell', validators=[Required()])
    
    max_pos = IntegerField('Max Position', validators=[Required()])

    capital_fund = FloatField('Capital Loss', validators=[Required()])

    loss_percentage = FloatField('Percentage Loss', validators=[Required()])
    
    validate = SubmitField('Validate')


class TestingForm(FlaskForm):
    
    Time_to_buy = TimeField("Buy at",format="%H:%M:%S",default=datetime(2000,1,1,0,0,0))

    Time_to_sell = TimeField("Sell at",format="%H:%M:%S",default=datetime(2000,1,1,0,0,0))

    Options = SelectField("Options",choices=[("0","Funding Rate Trades"),("1","1h"),("2","30min"),("3","15min")])

    Tp = FloatField("Take Profit",default=0)

    Sl = FloatField("Stop Loss", default=0)

    Length = IntegerField("Length",default=1)

    TimeFrame = SelectField("Timeframe",choices=[("0","Timeframe"),("1","Hour"),("2","Minute"),("3","Second")])

    RsiBuy = FloatField("RSI Buy",default=30)

    RsiSell = FloatField("RSI Sell",default=80)

    Capital = FloatField("Initial Capital",default=10000)
    
    Size = FloatField("Order Size",default=1000)

    submit_date = SubmitField('Submit')

    
    


    
