from flask import Flask
from flask_peewee.db import Database
from app import app
from auth import auth
# from flask import Blueprint, abort, request, Response, session, redirect, url_for, g
from peewee import IntegrityError

from admin import admin
from api import api
from views import *

app = Flask(__name__)
app.config.from_object('config.Configuration')
# app.config.from_object(__name__)

# Instantiate the db wrapper
db = Database(app)

admin.setup()
api.setup()

if __name__ == '__main__':
    print "Trying to create 'admin'!"
    auth.User.create_table(fail_silently=True)
    try:
        admin = auth.User(username='admin', email='', admin=True, active=True)
        admin.set_password('admin')
        admin.save()
        print "admin created!"
    except IntegrityError:
        print "User 'admin' already created!"

    app.debug = True
    app.run(host='0.0.0.0', port=8008)
