from auth import auth
from app import app
from flask import jsonify
from peewee import *
from functools import wraps
from flask import g, request, redirect, url_for, Response
import requests, json
from models import Card, Logrefill, Logpayment, Charge, User
import datetime





def custom_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        basic_auth = request.authorization
        if not basic_auth:
            return response_auth_failed()
        g.user = auth.authenticate(basic_auth.username, basic_auth.password)
        if not g.user:
            return response_auth_failed()

        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def homepage():
    return 'Welcome to A2B Restful API!'


@app.route('/private/')
@auth.login_required
def private_view():
    return 'This is private!'


@app.route('/custom/api/v0/refill/<int:card_id>', methods=['POST'])
@custom_login_required
def refill(card_id):
    if not request.json or 'credit' not in request.json:
        return Response('Missing credit parameter.', 400)

    # Get Card(vat, credit)
    card = Card.select(Card.credit).where(Card.id == card_id)
    if not card and not card[0]:
        return Response('Card not found.', 400)

    vat = card[0].vat

    credit = float(request.json['credit'])
    prev_credit = card[0].credit
    new_balance = prev_credit + credit
    Card.update(credit=new_balance).where(Card.id == card_id).execute()

    credit_without_vat = credit / (1 + vat / 100)

    # add logrefill
    logrefill = Logrefill(card=card_id, date=datetime.datetime.now, credit=credit, refill_type=0)
    logrefill.save()

    # add logpayment
    logpayment = Logpayment(card=card_id, date=datetime.datetime.now, payment=credit, payment_type=0, id_logrefill=logrefill.id)
    logpayment.save()

    # prepare dictionary for JSON return
    data = {
        'card_id': card_id,
        'current_balance': new_balance,
        'credit_without_vat': credit_without_vat,
        'credited': credit,
        'vat': card[0].vat,
        'logrefill_id': logrefill.id,
        'logpayment_id': logpayment.id
    }
    return jsonify(data)


@app.route('/custom/api/v0/extra_charge/<int:card_id>', methods=['POST'])
@custom_login_required
def extra_charge(card_id):
    if not request.json or 'amount' not in request.json:
        return Response('Missing amount parameter.', 400)

    # Get Card
    card = Card.select(Card.credit).where(Card.id == card_id)
    if not card and not card[0]:
        return Response('Card not found.', 400)

    amount = float(request.json['amount'])
    prev_credit = card[0].credit
    new_balance = prev_credit - amount
    Card.update(credit=new_balance).where(Card.id == card_id).execute()

    # add charge
    charge = Charge(id_cc_card=card_id, amount=amount, chargetype=4)
    charge.save()

    # prepare dictionary for JSON return
    data = {
        'card_id': card_id,
        'current_balance': new_balance,
        'amount': amount,
        'charge_id': charge.id
    }
    return jsonify(data)


# route to cretae a new user (registration)
@app.route('/custom/api/v0/register/', methods=['POST'])
def user_registration():
    req_data = request.get_json()
    if request.method == 'POST':  #this block is only entered when the form is submitted
        username = req_data['username']
        password = req_data['password']
        email = req_data['email']
        active = req_data['active']
        admin = req_data['admin']
        try:
        #    User.insert(req_data).execute()
            user = auth.User(username=username, email=email, admin=admin, active=active)
            user.set_password(password)
            user.save()
            data = {
                'result': 1
            }
        except IntegrityError as e:
            print(e)
            data = { 'result': 'Username already exists.' }
    else:
         data = { 'result': 'Not a post request.' }

    return jsonify(data)


@app.route('/custom/api/v0/login/', methods=['POST'])
def user_login():
    req_data = request.get_json()
    if request.method == 'POST':  #this block is only entered when the form is submitted
        username = req_data['username']
        password = req_data['password']
        try:

            if not request.json or 'username' not in request.json:
                return Response('Missing username parameter.', 400)

            # Get Card(vat, credit)
            user = User.select().where(User.username == username & User.password == password)
            if not user and not user[0]:
                return Response('User not found.', 400)

            email = user[0].email
            id = user[0].id
            active = user[0].active
            admin = user[0].admin
            data = {
                'result': 1,
                'username': username,
                'email': email,
                'active': active,
                'admin': admin
            }
        except NameError as e:
            print(e)
            data = { 'result': 'Name Error' }
    else:
         data = { 'result': 'Not a post request.' }

    return jsonify(data)



# user must have valid cognito access or ID token in header
@app.route('/custom/api/v0/user/fetch/', methods=['POST'])
def fetch_user():
    # get token value from header
    token = string(request.headers.get('Authorization'))

    headers = { 'Authorization' : 'Bearer ' + token }
    r = requests.get('https://redirect-app.auth.eu-west-2.amazoncognito.com/oauth2/userInfo', headers=headers, verify=False)
    j = json.loads(r.text)
    return jsonify(j)
