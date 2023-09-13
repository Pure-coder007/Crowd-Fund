from Shop import db, login_manager
from flask_login import UserMixin
# from flask_sqlalchemy import SQLAlchemy
# from Shop import app


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///funds.db'
# db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    items = db.relationship('Data', backref='owner', lazy='dynamic')
    fund_asked = db.relationship(
        'Fund', backref=db.backref('user_', lazy=True), lazy='dynamic'
    )
    
    
# Creating an admin
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



# Creating a database for our items
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # price = db.Column(db.Float(100), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(300), nullable=False)
    amount_needed = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # assuming user's model name is 'User'

    def __repr__(self):
        return f"UserRequest('{self.reason}', '{self.amount_needed}')"


class Fund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(200), nullable=False)
    amount_needed = db.Column(db.Float, nullable=False)
    amount_donated = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('user.id'), 
                        nullable=False)
    who_donated = db.relationship(
        'Donator', backref=db.backref('fund', lazy=True), lazy='dynamic'
    )
    
    
class Donator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    donation_amount = db.Column(db.Float, nullable=False)
    donating_for = db.Column(db.Integer, db.ForeignKey('fund.id')) # Assuming 'fund' is the tablename for the Fund model

