from flask import Flask
from flask_peewee.db import Database
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config.from_object('config.Configuration')

app.config['SECRET_KEY'] = os.environ.get('MAIL_SECRET_KEY')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')


# app.config.from_object(__name__)

# Instantiate the db wrapper
db = Database(app)
mail = Mail(app)
