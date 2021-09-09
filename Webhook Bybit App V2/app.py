
# TRADING APP FOR BYBIT V2 


# IMPORTS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import json,config_bybit
from datetime import datetime
import pytz
from Forms import InputsForm, LoginForm, TestingForm
from Testing import *
import pandas as pd 
import os
from FTXClient import *
from time import sleep


# ORDER METHODS
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Create a method for limit order

def order(market,side,price,size,postOnly=True,type='limit'):
    try:
        print(f"Sending order {type}- {side} - {price} - {size} - {market} ")
        order = FTXClient.place_order(market=market,side=side,price=price,size=size,type=type,post_only=postOnly)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False
    return order


def marketOrder(market,side,size,price=0,type='market'):
    try:
        print(f"Sending order {type}- {side} - {size} - {market} ")
        market_order = FTXClient.place_order(market=market,side=side,size=size,price=price,type=type)
    except Exception as e:
        print("An exception occured {}".format(e))
        return False
    return market_order


def triggerOrder(market,side,size,type,triggerPrice):
    try:
        if type == 'stop':
            print(f'Stop Loss hits. At {triggerPrice}')
        elif type == 'takeProfit':
            print(f'Take Profit hits. At {triggerPrice}')
        Order = FTXClient.place_conditional_order(market=market,side=side,size=size,type=type,trigger_price=triggerPrice)
    except Exception as e:
        print(f"An exception occured {e}")
        return False
    return Order
        
# FLASK SERVER
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Config flask app for local server
from flask import Flask, render_template, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy  
app = Flask(__name__)


db = SQLAlchemy(app) 
app.config['SECRET_KEY'] = ''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///NAME.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# All classes for database 
class Input(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    qty = db.Column(db.Integer, nullable=False)
    pips_buy = db.Column(db.Integer, nullable=False)
    pips_sell = db.Column(db.Integer, nullable=False)
    capital = db.Column(db.Integer, nullable=False)
    max_position = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)


    def __init__(self,qty,capital,max_position,percentage,pips_buy,pips_sell):
        self.qty = qty
        self.pips_buy = pips_buy
        self.pips_sell = pips_sell
        self.capital = capital
        self.max_position = max_position
        self.percentage = percentage

class Counter(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    count_orders = db.Column(db.Integer, default=0)
    count_sell = db.Column(db.Integer, default=0)
    count_buy = db.Column(db.Integer, default=0)
    count_cancelled = db.Column(db.Integer, default=0)
    count_exits = db.Column(db.Integer,default=0)
    


    def __init__(self):
        self.count_orders= 0
        self.count_buy= 0
        self.count_cancelled= 0
        self.count_sell= 0
        self.count_exits = 0
         


class Profit(db.Model):
    id = db.Column("id",db.Integer, primary_key=True)
    profit = db.Column(db.Float, nullable=False)
    gross_lose = db.Column(db.Float, nullable=False,default=0)
    gross_prof = db.Column(db.Float, nullable=False,default=0)

    def __init__(self):
        self.profit = 0 
        self.gross_lose = 0
        self.gross_prof = 0


# MUST CREATE THE AUTO CREATE FILE ALGO FOR DATABASE FILE
db_filename = "NAME.db"
db_file_exits = os.path.isdir(db_filename)
if not db_file_exits:
    db.create_all()

    


# ROUTES AND METHODS FOR TRADES
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Principal route
@app.route('/')
def welcome():
    page = "home"
    return render_template("Welcome.html",page=page)

# Page for enter inputs
@app.route("/Inputs", methods=['GET','POST'])  
def Inputs():
    stickValues = []
    form = InputsForm()
    if form.validate_on_submit():
        users = Input(qty=form.quantity.data,pips_buy=form.pips_buy.data,pips_sell=form.pips_sell.data,capital=form.capital_fund.data,max_position=form.max_pos.data,
                      percentage=form.loss_percentage.data)
        db.session.add(users)
        db.session.commit()
        flash('Validation correct. Update done!', 'success')
    return render_template('Inputs.html', title="Inputs", form= form,Candles=stickValues,apiKey=config_bybit.api_key,apiSecret=config_bybit.api_secret)

    

# Page for see inputs updated
@app.route("/view")
def view():
    return render_template("view.html", values=Input.query.all(), valide=Input.query.first(),title="View")

# Journal Page
@app.route("/journal", methods=['GET','POST'])
def journal():
    return render_template("journal.html", counter=Counter.query.all(), valide=Counter.query.first(), profit=Profit.query.all(), prof_val=Profit.query.first(), perc_prof=config_bybit.percentage_prof,title="Journal")

@app.route("/testing", methods=['GET','POST'])
def testing():
    markers = []
    totalTrade = 0
    values = [{'time':0,'value':0}]
    data_date = []
    data_prof = []
    data_sum = 0
    data_gross_prof = 0
    data_gross_lose = 0
    Wins = 0
    Loses = 0
    wins_doll = 0
    loses_doll = 0
    sum_doll = 0
    rsi = [{'time':0,'value':0}]
    form = TestingForm()
    if form.validate_on_submit():
        date_start = request.form['datestart']
        date_end = request.form['datend']
        value_options = int(request.form['Options'])
        value_rsi = int(request.form['TimeFrame'])
        capital = form.Capital.data
        size = form.Size.data
        sl = form.Sl.data
        tp = form.Tp.data
        if value_rsi != 0:
            data_chart = RSIStrat(form.RsiBuy.data,form.RsiSell.data,form.Length.data,date_start,date_end,sl,tp,capital,size) 
            values = data_chart[0]
            markers = data_chart[1]
            data_sum = data_chart[2]
            data_gross_prof = data_chart[3]
            data_gross_lose = data_chart[4]
            Wins = data_chart[5]
            Loses = data_chart[6]  
            rsi = data_chart[7]
        elif value_options != 0:
            data_chart = FundingStrat(request.form['Options'],date_start,date_end,sl,tp)
            values = data_chart[0]
            data_sum = data_chart[1]
            data_gross_lose = data_chart[2]
            data_gross_prof = data_chart[3]
            Loses = data_chart[4]
            Wins = data_chart[5]
            sum_doll = data_chart[6]
            wins_doll = data_chart[7]
            loses_doll = data_chart[8]
        else:
            data_chart = SimpleStrat(form.Time_to_buy.data,form.Time_to_sell.data,date_start,date_end,sl,tp,capital,size)    
            values = data_chart[0]
            data_sum = data_chart[1]
            totalTrade = data_chart[2]
            data_gross_lose = data_chart[3]
            data_gross_prof = data_chart[4]
            Loses = data_chart[5]
            Wins = data_chart[6]
            sum_doll = data_chart[7]
            wins_doll = data_chart[8]
            loses_doll = data_chart[9]
  
    return render_template("testing.html",form=form,times=data_date, profits=data_prof,sum=data_sum,totalTrades=totalTrade,gross_lose=data_gross_lose,gross_prof=data_gross_prof,wins=Wins,loses=Loses,dollarSum=sum_doll,dollarWins=wins_doll,dollarLoses=loses_doll,values=values,markers=markers,rsi=rsi,title="Testing")


# Create a route for webhook POST request 
@app.route('/webhook', methods=['POST'])
def webhook():

    # print out infos avout server
    print(request)
    data = json.loads(request.data)
    
    # CHECKING PASSWORD ALERT
    #----------------------------------------------------------------------------------------------------------
    
    # Set if condition for passwrod webhook 
    if data["passphrase"] != config_bybit.webhook_password:
        print("Invalid password! Please checks logs.")
        
        return {
            'code':'Error Login',
            'message':'Password Invalid'
            }
    
   
    # VALIDATION AND CREATION INPUTS
    #----------------------------------------------------------------------------------------------------------
   
    # Check if inputs are correctly entered
    found_inputs = Input.query.all()
    if not found_inputs:
        print("Inputs are not defined. Please enter inputs!")
        return{
            'code':'Error Inputs.',
            'message':'Inputs are not defined.'
            }

    # Get the last vcalues into the table and put it into variables for create orders
    for item in found_inputs:
        qty_data = item.qty
        pips_data_b = item.pips_buy
        pips_data_s = item.pips_sell
        capital_data = item.capital
        max_pos_data = item.max_position
        perc_data = item.percentage
    
    
    # Symbol: BTCUSD
    symbol_data = data["ticker"]
    # Price close
    price_data = data["strategy"]["order_price"]
    # Buy or Sell
    side_data = data["strategy"]["order_action"]
    # Get the order id
    orders_id = data['strategy']['order_id']
    # Create a capital limit loss profit
    price_pos = data['bar']['close']
    


    # Update price close regarding if sell or buy signal (half pips)
    
    if side_data == 'sell':
        price_data = price_data + pips_data_s
    elif side_data == 'buy':
        price_data = price_data - pips_data_b


     # Get the wallet balance of account
    available = FTXClient.get_balances()[0]['total']
    print('SOME INFORMATIONS ABOUT THE WALLET BALANCE: ')
    print(f"Available Wallet Balance ===> {available}")

    percentLoss = capital_data - (1 / 100)
    capital_loss = (available * percentLoss) - available
    

    if available == capital_loss:
        print("Capital loss hited! At ${capital_loss}.")
        return{
            'code':"Algo stop.",
            'message':'Capital loss hited.'
            }

    # Get size and side position 
    size = FTXClient.get_position(name='SOL-PERP')['size']
    side = FTXCLient.get_position(name='SOL-PERP')['side']
    
    print(f"Current size ===> {size}, side ==> {side}")
    
    # DEFINE MAX POSITION SIZE
    #----------------------------------------------------------------------------------------------------------

    # Check stop loss size position
  
    

    # ORDERS AND METHODS
    #----------------------------------------------------------------------------------------------------------

    # Create an instance of Counter class
    c = Counter.query.first()
    count = 0
    cancelled = False
    if orders_id == 'Exit Position':
        config_bybit.sizeRebalanced = True
        order_response = marketOrder('SOL-PERP',side_data,size)
        print(f"This is a trigger order at {price_data}")
        if not c:
            c = Counter()
            c.count_exits += 1
            db.session.add(c)
        c.count_exits += 1 
        db.session.commit()
    else:
        print("The size is rebalanced:",config_bybit.sizeRebalanced)
        if config_bybit.sizeRebalanced == True:
            qty_data = 1
            print('The size rebalanced is actived.')
        order_response = order('SOL-PERP',side_data,price_data,qty_data)
        while True:
            count += 1
            print(f"Counter loop: {count}")
            ID = order_response['id']
            sleep(10)
            fillSize = FTXClient.get_order_history('SOL-PERP',side_data,'limit')[0]['filledSize']
            try:
                if fillSize == 0:
                    cancelled_order = FTXClient.cancel_order(ID)
                    LP = FTXClient.get_market('SOL-PERP')['last']
                    print("The order have not been filled yet.")
                    order_response = order('SOL-PERP',side_data,LP,qty_data)
                    
                else:
                    config_bybit.sizeRebalanced = False
                    break
            except Exception as a:
                print(f"Problem occured ==> {a}")
                cancelled = True
                if count == 1:
                    if not c:
                        c = Counter()
                        c.count_cancelled += 1 
                        db.session.add(c)
                    c.count_cancelled += 1 
                    db.session.commit()
                LP = FTXClient.get_market('SOL-PERP')['last']
                print("The order has been cancelled.")
                order_response = order('SOL-PERP',side_data,LP,qty_data)
            if count == 4 :
                order_response = marketOrder('SOL-PERP',side_data,qty_data)
                config_bybit.sizeRebalanced = False
                break
        

    
    #Track the open interest
    print("INFORMATIONS ABOUT MARKET: ")
    
    
   # pnlRealised = FTXClient.get_position(name='EOS-PERP')['realizedPnl']

    try:
        config_bybit.percentage_prof = round((qty_data * 0.01) / P.profit,2)
    except:
        print("Profit zero.")
    
    # Updates counts for sell and buy orders
    if side_data == "sell" and cancelled != True:
        if not c:
            c = Counter()
            c.count_sell += 1
            db.session.add(c)
        c.count_sell += 1 
        db.session.commit()
    if side_data == "buy" and cancelled != True:
        if not c:
            c = Counter()
            c.count_buy += 1 
            db.session.add(c)
        c.count_buy += 1 
        db.session.commit()

    print(f"Exits Position ==> {c.count_exits}")
    print(f"Cancelled orders ==> {c.count_cancelled}")
    print(f"Sell orders ==> {c.count_sell}")
    print(f"Buy orders ==> {c.count_buy}")


    # When the request will reach the server return a response
    if order_response: 
        if not c:
            c = Counter()
            c.count_orders += 1
            db.session.add(c)
        c.count_orders += 1
        db.session.commit()
        print(f"Orders went through ==> {c.count_orders}") 
        return{
            "code":"Success",
            "message": f"Order excecuted, {side_data}"
            }
    else:
        print("Order failed.")
        return {
            "code": "Error",
            "message": "Order failed."
            }

       
 
    #---------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if __name__ == '__main__':
        app.run(debug=True)
        
        