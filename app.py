from flask import Flask, render_template, redirect, url_for, flash, session, request
import random
from flask_sqlalchemy import SQLAlchemy
from models import User,db, Stocks,Investment,Transaction
from flask_login import LoginManager, login_user, current_user, logout_user,login_required
from seed import seed_data
from forms import RegistrationForm, LoginForm,StockFilterForm,InvestmentForm
from flask_migrate import Migrate
from stock_utils import get_historical_stock_price
from datetime import datetime
from flask_bcrypt import Bcrypt

# Create Flask application
app = Flask(__name__)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# app.config
app.config['SECRET_KEY'] = 'jisoo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///stocksimul_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# setting for LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "You have to login to access here"
login_manager.login_message_category = "info"

# create table from app_context
with app.app_context():
    db.create_all()
    # insert data
    seed_data()

# user Loading
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('userpage'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('userpage'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.','info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('userpage'))
        
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # 기존 사용자 확인
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username is already in use.', 'danger')
            else:
                flash('Email address is already in use.', 'danger')
            return render_template('register.html', form=form)
        
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                username=form.username.data,
                password=hashed_password,
                email=form.email.data
            )
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Registration completed successfully!', 'success')
            return redirect(url_for('userpage'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', form=form)
        
    return render_template('register.html', form=form)
        

        
    return render_template('register.html', form=form)

@app.route('/profile')
def userpage():
    return render_template('userpage.html')

@app.route('/invest', methods=['POST','GET'])
@login_required
def invest():
    stocks = Stocks.query.all()
    return render_template('invest.html',stocks = stocks)

@app.route('/start_simulation', methods=['GET', 'POST'])
@login_required
def start_simulation():
    def set_session_data(investment):
        session['current_year']= investment.current_year
        session['current_budget']= investment.total_assets
        session['round'] = investment.round_number

    investment = Investment.query.filter_by(
        user_id =current_user.id,
        status ="in_progress").first()  

    if not investment:
        Start_year_MIN,Start_year_MAX = 2010,2018
        start_year = random.randint(Start_year_MIN,Start_year_MAX)
        starting_budget = 10000

        investment = Investment(
            user_id = current_user.id,
            round_number = 1,
            total_assets = starting_budget,
            current_year = start_year,
            status = "in_progress"
        )
        db.session.add(investment)
        db.session.commit()
    
        set_session_data(investment)
        flash(f"New simulation started for {start_year}", "success")
    else:
        set_session_data(investment)
        flash(f"Existing investment session loaded from {investment.current_year}!", "info")

    return redirect(url_for('investment_detail'))

@app.route('/investment_detail')
@login_required
def investment_detail():
    current_round = session.get('round', 1)
    current_year = session.get('current_year', 2010)
    current_budget = session.get('current_budget', 10000)

    investment = Investment.query.filter_by(
        user_id=current_user.id,
        status="in_progress"
    ).first()
    
    if not investment:
        flash("No ongoing investment found.", "danger")
        return redirect(url_for('invest'))

    stock_holdings = {}
    for transaction in investment.transactions:
        symbol = transaction.stock.symbol
        if symbol not in stock_holdings:
            stock_holdings[symbol] = {
                'quantity': 0,
                'company_name': transaction.stock.company_name,
                'current_price': 0,
                'total_value': 0
            }
        
        if transaction.transaction_type == "buy":
            stock_holdings[symbol]['quantity'] += transaction.quantity
        else:
            stock_holdings[symbol]['quantity'] -= transaction.quantity

    stock_holdings = {k: v for k, v in stock_holdings.items() if v['quantity'] > 0}

    total_stock_value = 0
    for symbol, holding in stock_holdings.items():
        current_price = get_historical_stock_price(symbol, current_year, 1)
        if current_price:
            holding['current_price'] = current_price
            holding['total_value'] = current_price * holding['quantity']
            total_stock_value += holding['total_value']
            holding['formatted_price'] = f"${current_price:.2f}"
            holding['formatted_total'] = f"${holding['total_value']:.2f}"

    total_assets = current_budget + total_stock_value

    return render_template('investment_detail.html',
                         current_round=current_round,
                         current_year=current_year,
                         current_budget=f"${current_budget:.2f}",
                         stock_holdings=stock_holdings,
                         total_stock_value=f"${total_stock_value:.2f}",
                         total_assets=f"${total_assets:.2f}")

@app.route('/view_investment_history')
@login_required
def view_investment_history():
    finished_investments = Investment.query.filter_by(
        user_id=current_user.id,
        status="finished"
    ).order_by(Investment.end_date.desc()).all()
    
    return render_template(
        'view_investment_history.html',
        investments=finished_investments
    )

@app.route('/stocks', methods=['GET', 'POST'])
@login_required
def stocks():    
    form = StockFilterForm()
    
    sectors = db.session.query(Stocks.sector).distinct().all()
    form.sector.choices = [(s[0], s[0]) for s in sectors]

    stocks = []
    if form.validate_on_submit():
        selected_sector = form.sector.data
        stocks = Stocks.query.filter_by(sector=selected_sector).all()
    else:
        stocks = Stocks.query.all()  # Display all stocks by default

    return render_template('stocks.html', form=form, stocks=stocks, sectors=sectors)

@app.route('/stock_detail/<symbol>', methods=['GET', 'POST'])
@login_required
def stock_detail(symbol):
    form = InvestmentForm()  
    stock = Stocks.query.filter_by(symbol=symbol).first()
    current_year = session.get('current_year', 2010)  
    current_round = session.get('round', 1)
    budget = session.get('current_budget', 10000)

    if not stock:
        flash("Stock not found.", "danger")
        return redirect(url_for('stocks'))

    session['symbol'] = symbol

    current_price = get_historical_stock_price(symbol, current_year, 1)
    if current_price is None:
        flash("Unable to retrieve current stock price.", "danger")
        current_price = "N/A"
        max_quantity = 0
    else:
        current_price = float(current_price)
        max_quantity = int(budget / current_price)
        current_price = f"{current_price:.2f}"

    session['current_price'] = current_price

    return render_template('stock_detail.html', 
                         form=form, 
                         stock=stock, 
                         current_price=current_price, 
                         current_year=current_year, 
                         current_round=current_round,
                         budget=budget,
                         max_quantity=max_quantity)

@app.route('/buy_or_sell', methods=['POST'])
@login_required
def buy_or_sell():
    form = InvestmentForm()
    if form.validate_on_submit():
        symbol = session.get('symbol')
        if not symbol:
            flash('Stock symbol not found.', 'danger')
            return redirect(url_for('invest'))
            
        action = request.form.get('action')
        quantity = int(form.quantity.data)
        
        stock = Stocks.query.filter_by(symbol=symbol).first()
        if not stock:
            flash('Stock not found.', 'danger')
            return redirect(url_for('invest'))
        
        investment = Investment.query.filter_by(
            user_id=current_user.id,
            status="in_progress"
        ).first()
        
        if not investment:
            flash('No ongoing investment found.', 'danger')
            return redirect(url_for('invest'))
        
        try:
            current_price = float(session.get('current_price', 0))
            total_cost = float(current_price * quantity)
            current_assets = float(investment.total_assets)
        except (TypeError, ValueError):
            flash('Invalid price information.', 'danger')
            return redirect(url_for('stock_detail', symbol=symbol))
        
        if action == 'buy':
            if total_cost > current_assets:
                flash('Insufficient balance.', 'danger')
                return redirect(url_for('stock_detail', symbol=symbol))
            
            transaction = Transaction(
                investment_id=investment.id,
                stock_id=stock.id,
                transaction_type='buy',
                quantity=quantity,
                price=current_price
            )
            
            investment.total_assets = current_assets - total_cost
            session['current_budget'] = investment.total_assets
            
        elif action == 'sell':
            owned_quantity = 0
            for trans in investment.transactions:
                if trans.stock_id == stock.id:
                    if trans.transaction_type == 'buy':
                        owned_quantity += trans.quantity
                    else:
                        owned_quantity -= trans.quantity
            
            if quantity > owned_quantity:
                flash('Cannot sell more shares than owned.', 'danger')
                return redirect(url_for('stock_detail', symbol=symbol))
            
            transaction = Transaction(
                investment_id=investment.id,
                stock_id=stock.id,
                transaction_type='sell',
                quantity=quantity,
                price=current_price
            )
            
            investment.total_assets += total_cost
            session['current_budget'] = investment.total_assets
        
        try:
            db.session.add(transaction)
            db.session.commit()
            flash(f'{action} {quantity} shares of {symbol} at ${current_price:.2f}', 'success')
            return redirect(url_for('investment_detail'))
        except Exception as e:
            db.session.rollback()
            flash('Error occurred during transaction.', 'danger')
            return redirect(url_for('stock_detail', symbol=symbol))
    
    flash('Form validation failed.', 'danger')
    return redirect(url_for('stock_detail', symbol=symbol))



@app.route('/next_round', methods=['POST'])
@login_required
def next_round():
    current_round = session.get('round', 1)
    
    if current_round < 5:
        session['round'] = current_round + 1
        session['current_year'] = session.get('current_year') + 1
        
        investment = Investment.query.filter_by(
            user_id=current_user.id,
            status="in_progress"
        ).first()
        
        if investment:
            investment.round_number = session['round']
            investment.current_year = session['current_year']
            investment.total_assets = session['current_budget']
            db.session.commit()
            
        return redirect(url_for('investment_detail'))
    else:
        return redirect(url_for('finish_game'))

@app.route('/finish_game', methods=['POST'])
@login_required
def finish_game():
    investment = Investment.query.filter_by(
        user_id=current_user.id,
        status="in_progress"
    ).first()
    
    if investment:
        stock_holdings = {}
        for transaction in investment.transactions:
            symbol = transaction.stock.symbol
            if symbol not in stock_holdings:
                stock_holdings[symbol] = {
                    'quantity': 0,
                    'stock': transaction.stock
                }
            
            if transaction.transaction_type == "buy":
                stock_holdings[symbol]['quantity'] += transaction.quantity
            else:
                stock_holdings[symbol]['quantity'] -= transaction.quantity

        total_stock_value = 0
        current_year = session.get('current_year', 2010)
        for symbol, holding in stock_holdings.items():
            if holding['quantity'] > 0:
                current_price = get_historical_stock_price(symbol, current_year, 1)
                if current_price:
                    total_stock_value += float(current_price * holding['quantity'])

        current_budget = float(session.get('current_budget', 0))
        final_assets = current_budget + total_stock_value
        
        initial_budget = 10000
        profit_rate = ((final_assets - initial_budget) / initial_budget) * 100
        end_date = datetime(current_year+4,1,2)
        
        investment.status = "finished"
        investment.profit_rate = profit_rate
        investment.total_assets = final_assets
        investment.end_date =  end_date
        
        db.session.commit()
        
        session.pop('round', None)
        session.pop('current_year', None)
        session.pop('current_budget', None)
        
        flash(f'Game over! Final profit rate: {profit_rate:.2f}%', 'success')
        return redirect(url_for('view_investment_history'))
    
    flash('No ongoing game found.', 'danger')
    return redirect(url_for('invest'))

if __name__ == '__main__':
    app.run(debug=True)