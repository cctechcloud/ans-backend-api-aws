from app import app
from auth import auth
# from flask import Blueprint, abort, request, Response, session, redirect, url_for, g
from peewee import IntegrityError

from admin import admin
from api import api
from views import *

admin.setup()
api.setup()

@app.route('/status', methods=['GET', 'POST'])
def status():
  status =  "This web api service is up and running!"
  return status

@app.route('/addadmin', methods=['GET', 'POST'])
def addadmin():
  admin = auth.User(username='cctechadmin', email='cctechcloud@yahoo.com', admin=True, active=True)
  admin.set_password('cctechpass')
  admin.save()
  status =  "admin user added!"
  return status

if __name__ == '__main__':
    #auth.User.create_table(fail_silently=True)
    # Note.create_table(fail_silently=True)
    try:
        #admin = auth.User(username='admin', email='', admin=True, active=True)
        #admin.set_password('admin')
        #admin.save()
        print "Trying to create User 'admin'!"
    except IntegrityError:
        print "User 'admin' already created!"

    app.debug = True
    app.run(host='0.0.0.0', port=8008)
