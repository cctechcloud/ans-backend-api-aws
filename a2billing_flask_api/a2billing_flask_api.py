from app import app
from auth import auth
# from flask import Blueprint, abort, request, Response, session, redirect, url_for, g
from peewee import IntegrityError

#from admin import admin
#from api import api
from views import *

admin.setup()
api.setup()



if __name__ == '__main__':
    # Note.create_table(fail_silently=True)

    try:
        print("User admin already existing!")
    except IntegrityError:
        print("User admin already created!")

    app.debug = True
    app.run(host='0.0.0.0', port=8008)

#@app.route('/status', methods=['GET', 'POST'])
#def status():
 # status =  "This web api service is up and running!"
  #return status

#@app.route('/addadmin', methods=['GET', 'POST'])
#def addadmin():
  #auth.User.create_table(fail_silently=True)
  #admin = auth.User(username='admin', email='admin@yahoo.com', admin=True, active=True)
  #admin.set_password('admin')
  #admin.save()
  #status =  "admin user added!"
  #return status
