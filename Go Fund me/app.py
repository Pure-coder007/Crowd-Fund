from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

app.config['SECRET_KEY'] = '2d8926762ccbac889d55b32635333a91'



cloudinary.config(  
  cloud_name = "duyoxldib", 
  api_key = "778871683257166", 
  api_secret = "NM2WHVuvMytyfnVziuzRScXrrNk" 
)

DB_PATH = os.environ.get('SQLITE_DB_PATH', 'sqlite:///mydatabase.db')  # Default SQLite path
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SECRET_KEY'] = '1e04deb868b1640f313bbb8c680f3d49'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "kingsleydike318@gmail.com"
app.config['MAIL_PASSWORD'] = 'byyhvorltumsxffq'
mail = Mail(app)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from app import routes