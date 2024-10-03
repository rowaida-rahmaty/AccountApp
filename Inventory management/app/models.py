from flask_login import UserMixin
from datetime import datetime
from app import db  # Make sure to import the db instance her




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    @staticmethod
    def get_all_products(user_id):
        return Product.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.filter_by(id=product_id).all()

    @staticmethod
    def check_stock(product_id, user_id):
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        return product.quantity if product else None

    @staticmethod
    def is_reorder_needed(product_id, user_id):
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        return product.quantity <= product.reorder_level if product else False
    

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(100))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    @staticmethod
    def get_supplier_info(supplier_id):
        return Supplier.query.get(supplier_id)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update_balance(self, amount, transaction_type):
        if transaction_type == "DEBIT":
            self.balance -= amount
        elif transaction_type == "CREDIT":
            self.balance += amount
        db.session.commit()

    @staticmethod
    def get_balance(account_name):
        account = Account.query.filter_by(account_name=account_name).first()
        return account.balance if account else None


class FinancialTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)

    def record(self):
        db.session.add(self)
        account = Account.query.get(self.account_id)
        if self.transaction_type == "DEBIT":
            account.balance -= self.amount
        elif self.transaction_type == "CREDIT":
            account.balance += self.amount
        db.session.commit()

    @staticmethod
    def get_transaction_history(account_id):
        return FinancialTransaction.query.filter_by(account_id=account_id).order_by(FinancialTransaction.date.desc()).all()
from datetime import datetime


class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_changed = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def record(self):
        db.session.add(self)
        product = Product.query.get(self.product_id)
        if self.transaction_type == "IN":
            product.quantity += self.quantity_changed
        elif self.transaction_type == "OUT":
            product.quantity -= self.quantity_changed
        db.session.commit()

    @staticmethod
    def get_transaction_history(product_id):
        return InventoryTransaction.query.filter_by(product_id=product_id).all()
