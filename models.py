from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, username, password):
        """User authenticate"""
        user = cls.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    def __repr__(self):
        return f"<User id={self.id} username={self.username} email={self.email}>"


class Stocks(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    company_name = db.Column(db.String, nullable=False)
    sector = db.Column(db.String, nullable=False)

    transactions = db.relationship('Transaction', back_populates='stock')

    def __repr__(self):
        return f"<Stocks id={self.id} symbol={self.symbol} company_name={self.company_name} sector={self.sector}>"


class Investment(db.Model):
    __tablename__ = 'investments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    total_assets = db.Column(db.Float, nullable=True)
    status = db.Column(db.String, nullable=False, default="in_progress", server_default="in_progress")
    current_year = db.Column(db.Integer, nullable=False)
    profit_rate = db.Column(db.Float)
    end_date = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('investments', cascade='all, delete-orphan'))
    transactions = db.relationship('Transaction', backref='investment', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Investment id={self.id} user_id={self.user_id} round_number={self.round_number} status={self.status} current_year={self.current_year}>"


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id'), nullable=False)  # Investment와 연결
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)  # Stocks와 연결
    transaction_type = db.Column(db.String, nullable=False)  # buy 또는 sell
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # 관계 설정
    stock = db.relationship('Stocks', back_populates='transactions')  # Stocks와의 관계 설정

    def __repr__(self):
        return f"<Transaction id={self.id} stock_id={self.stock_id} type={self.transaction_type} quantity={self.quantity} price={self.price}>"