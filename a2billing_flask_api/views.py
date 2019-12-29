from auth import auth
from app import app
from flask import jsonify
from peewee import *
from functools import wraps
from flask import g, request, redirect, url_for, Response, Flask, abort
import requests, json
from models import Card, Logrefill, Logpayment, Charge, User, Did, DidDestination, CountryServer, SipBuddies, Ticket, TicketComment, Country
import datetime
from flask_cognito import *
import hmac
import hashlib
import base64
from twilio.rest import Client
import random
import os




country_code_dict = {"BD": "Bangladesh", "BE": "Belgium", "BF": "Burkina Faso", "BG": "Bulgaria", "BA": "Bosnia and Herzegovina", "BB": "Barbados", "WF": "Wallis and Futuna", "BL": "Saint Barthelemy", "BM": "Bermuda", "BN": "Brunei", "BO": "Bolivia", "BH": "Bahrain", "BI": "Burundi", "BJ": "Benin", "BT": "Bhutan", "JM": "Jamaica", "BV": "Bouvet Island", "BW": "Botswana", "WS": "Samoa", "BQ": "Bonaire, Saint Eustatius and Saba ", "BR": "Brazil", "BS": "Bahamas", "JE": "Jersey", "BY": "Belarus", "BZ": "Belize", "RU": "Russia", "RW": "Rwanda", "RS": "Serbia", "TL": "East Timor", "RE": "Reunion", "TM": "Turkmenistan", "TJ": "Tajikistan", "RO": "Romania", "TK": "Tokelau", "GW": "Guinea-Bissau", "GU": "Guam", "GT": "Guatemala", "GS": "South Georgia and the South Sandwich Islands", "GR": "Greece", "GQ": "Equatorial Guinea", "GP": "Guadeloupe", "JP": "Japan", "GY": "Guyana", "GG": "Guernsey", "GF": "French Guiana", "GE": "Georgia", "GD": "Grenada", "GB": "United Kingdom", "GA": "Gabon", "SV": "El Salvador", "GN": "Guinea", "GM": "Gambia", "GL": "Greenland", "GI": "Gibraltar", "GH": "Ghana", "OM": "Oman", "TN": "Tunisia", "JO": "Jordan", "HR": "Croatia", "HT": "Haiti", "HU": "Hungary", "HK": "Hong Kong", "HN": "Honduras", "HM": "Heard Island and McDonald Islands", "VE": "Venezuela", "PR": "Puerto Rico", "PS": "Palestinian Territory", "PW": "Palau", "PT": "Portugal", "SJ": "Svalbard and Jan Mayen", "PY": "Paraguay", "IQ": "Iraq", "PA": "Panama", "PF": "French Polynesia", "PG": "Papua New Guinea", "PE": "Peru", "PK": "Pakistan", "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland", "PM": "Saint Pierre and Miquelon", "ZM": "Zambia", "EH": "Western Sahara", "EE": "Estonia", "EG": "Egypt", "ZA": "South Africa", "EC": "Ecuador", "IT": "Italy", "VN": "Vietnam", "SB": "Solomon Islands", "ET": "Ethiopia", "SO": "Somalia", "ZW": "Zimbabwe", "SA": "Saudi Arabia", "ES": "Spain", "ER": "Eritrea", "ME": "Montenegro", "MD": "Moldova", "MG": "Madagascar", "MF": "Saint Martin", "MA": "Morocco", "MC": "Monaco", "UZ": "Uzbekistan", "MM": "Myanmar", "ML": "Mali", "MO": "Macao", "MN": "Mongolia", "MH": "Marshall Islands", "MK": "Macedonia", "MU": "Mauritius", "MT": "Malta", "MW": "Malawi", "MV": "Maldives", "MQ": "Martinique", "MP": "Northern Mariana Islands", "MS": "Montserrat", "MR": "Mauritania", "IM": "Isle of Man", "UG": "Uganda", "TZ": "Tanzania", "MY": "Malaysia", "MX": "Mexico", "IL": "Israel", "FR": "France", "IO": "British Indian Ocean Territory", "SH": "Saint Helena", "FI": "Finland", "FJ": "Fiji", "FK": "Falkland Islands", "FM": "Micronesia", "FO": "Faroe Islands", "NI": "Nicaragua", "NL": "Netherlands", "NO": "Norway", "NA": "Namibia", "VU": "Vanuatu", "NC": "New Caledonia", "NE": "Niger", "NF": "Norfolk Island", "NG": "Nigeria", "NZ": "New Zealand", "NP": "Nepal", "NR": "Nauru", "NU": "Niue", "CK": "Cook Islands", "XK": "Kosovo", "CI": "Ivory Coast", "CH": "Switzerland", "CO": "Colombia", "CN": "China", "CM": "Cameroon", "CL": "Chile", "CC": "Cocos Islands", "CA": "Canada", "CG": "Republic of the Congo", "CF": "Central African Republic", "CD": "Democratic Republic of the Congo", "CZ": "Czech Republic", "CY": "Cyprus", "CX": "Christmas Island", "CR": "Costa Rica", "CW": "Curacao", "CV": "Cape Verde", "CU": "Cuba", "SZ": "Swaziland", "SY": "Syria", "SX": "Sint Maarten", "KG": "Kyrgyzstan", "KE": "Kenya", "SS": "South Sudan", "SR": "Suriname", "KI": "Kiribati", "KH": "Cambodia", "KN": "Saint Kitts and Nevis", "KM": "Comoros", "ST": "Sao Tome and Principe", "SK": "Slovakia", "KR": "South Korea", "SI": "Slovenia", "KP": "North Korea", "KW": "Kuwait", "SN": "Senegal", "SM": "San Marino", "SL": "Sierra Leone", "SC": "Seychelles", "KZ": "Kazakhstan", "KY": "Cayman Islands", "SG": "Singapore", "SE": "Sweden", "SD": "Sudan", "DO": "Dominican Republic", "DM": "Dominica", "DJ": "Djibouti", "DK": "Denmark", "VG": "British Virgin Islands", "DE": "Germany", "YE": "Yemen", "DZ": "Algeria", "US": "United States", "UY": "Uruguay", "YT": "Mayotte", "UM": "United States Minor Outlying Islands", "LB": "Lebanon", "LC": "Saint Lucia", "LA": "Laos", "TV": "Tuvalu", "TW": "Taiwan", "TT": "Trinidad and Tobago", "TR": "Turkey", "LK": "Sri Lanka", "LI": "Liechtenstein", "LV": "Latvia", "TO": "Tonga", "LT": "Lithuania", "LU": "Luxembourg", "LR": "Liberia", "LS": "Lesotho", "TH": "Thailand", "TF": "French Southern Territories", "TG": "Togo", "TD": "Chad", "TC": "Turks and Caicos Islands", "LY": "Libya", "VA": "Vatican", "VC": "Saint Vincent and the Grenadines", "AE": "United Arab Emirates", "AD": "Andorra", "AG": "Antigua and Barbuda", "AF": "Afghanistan", "AI": "Anguilla", "VI": "U.S. Virgin Islands", "IS": "Iceland", "IR": "Iran", "AM": "Armenia", "AL": "Albania", "AO": "Angola", "AQ": "Antarctica", "AS": "American Samoa", "AR": "Argentina", "AU": "Australia", "AT": "Austria", "AW": "Aruba", "IN": "India", "AX": "Aland Islands", "AZ": "Azerbaijan", "IE": "Ireland", "ID": "Indonesia", "UA": "Ukraine", "QA": "Qatar", "MZ": "Mozambique"}
inv_country_code_dict = {v: k for k, v in country_code_dict.items()}


def receipt_webhook():
    data = request.get_data()
    if not data:
        abort(401)
    return Response('Webhook recieved with request data', 200)


# decorater for basic authentication.
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

# Don't hardcode. Load it from Environment variable.
SECRET = b'877e81cd18f9d8cd2d5bdf72bc82ddc33f26678507895bf81c853132f0ae6725'

def verify_webhook(data, hmac_header):
    print(" **** data from verify_webhook ****")
    print(data)
    print(type(data))
    print(hmac_header)
    print(type(hmac_header))
    digest = hmac.new(SECRET, data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

# ***** function to check avaiibile phone numbers in the country ******
def onboarding(country, email, amount, order_number, ticket_id, destination):

    country_code = inv_country_code_dict[country]

    # step 1 :  check and buy a phone number for a country under Twilio account
    # Don't hardcode. Load it from Environment variable.
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    default_address_sid = "Address SID for default address"
    client = Client(account_sid, auth_token)

    numbers = client.available_phone_numbers(country_code).local.list(
                                                            limit=10
                                                        )
    while numbers:
        available_phone_number = numbers.pop(-1).phone_number
        stripped_available_phone_number =  available_phone_number.lstrip('+')

        query = Card.select(Card.id).where(Card.username == stripped_available_phone_number)
        card = query.execute()
        if not card:
            account_number = stripped_available_phone_number
            break
    print("New Phone number " + account_number + " has been selected")


    '''
    available_phone_number = numbers[0].phone_number
    stripped_available_phone_number =  available_phone_number.lstrip('+')

    query = Card.select(Card.id).where(Card.username == stripped_available_phone_number)
    card = query.execute()

    if not card:
        account_number = stripped_available_phone_number
    else:
        available_phone_number = numbers[1].phone_number
        stripped_available_phone_number = available_phone_number.lstrip('+')
        account_number = stripped_available_phone_number

    '''

    '''
    address = client.addresses.create(
                                customer_name='redirect',
                                street='miles east',
                                city='didcot',
                                region='oxford',
                                postal_code='OX11 6EE',
                                iso_country='GB'
                            )


    # Purchase the phone number
    incoming_phone_number = client.incoming_phone_numbers \
                .create(phone_number=available_phone_number, address_sid=default_address_sid) \
                .update(voice_url=os.environ.get("REDIRECT_VOICE_URL"))

    inbound_phone_number =  str(incoming_phone_number.phone_number)
    account_number = inbound_phone_number.lstrip('+')
    '''
   # *****  create A2B card for that phone number, create DiD, create DidDestination  ******

    pin = random.randint(1000,9999)
    passcode = email + str(pin)
    # step 2 : Create Card
    card = Card.create(username= account_number, useralias= account_number, uipass= passcode, email= email, sip_buddy= 1, lock_pin= pin, country= country_code, expiredays= '30', enableexpire= '1')
    print(card.username)       #
    add_ticket_comment("Card created with id: " + str(card.id) + " and username: " + account_number + " and country: " + country, order_number, ticket_id)

    query_id_country = Country.select(Country.id).where(Country.countryname == country)
    id_country = query_id_country.execute()
    if id_country:
        id_cc_country = str(id_country[0].id)
        print(id_cc_country)
    else:
        id_cc_country = '224'

    # step 3 :  create a DID in a2billing
    did = Did.create(
                            id_cc_didgroup= account_number,
                            did= account_number,
                            id_cc_country= id_cc_country,
                            iduser= Card.id,
                            selling_rate= 0.03,
                            max_concurrent= 2,
                            startingdate= str(datetime.datetime.now()),
                            billingtype= 0,
                            fixrate= amount,
                            aleg_carrier_cost_min = 0.016,
                            aleg_carrier_cost_min_offp = 0.016,
                            aleg_carrier_increment = 60,
                            aleg_carrier_increment_offp = 60,
                            aleg_carrier_initblock = 60,
                            aleg_carrier_initblock_offp = 60,
                            aleg_retail_cost_min = 0.03,
                            aleg_retail_cost_min_offp = 0.03,
                            aleg_retail_increment = 60,
                            aleg_retail_increment_offp = 60,
                            aleg_retail_initblock = 60,
                            aleg_retail_initblock_offp = 60
                        )
    add_ticket_comment("DiD created - did: " + str(did.did), order_number, ticket_id)
    # step 3 :  create a DID destination using customer phone number in a2billing
    stripped_destination = destination.lstrip('+')
    # sip/linphone destination
    did_destination_1 = DidDestination.create(destination= 'SIP/' + destination + '@sip.linphone.org', priority= 1, id_cc_card= card.id, id_cc_did= did.id, activated= 1, voip_call= 1, validated= 0)
    # PSTN destination
    did_destination_2 = DidDestination.create(destination= stripped_destination, priority= 2, id_cc_card= card.id, id_cc_did= did.id, activated= 1, voip_call= 0, validated= 0)

    add_ticket_comment("DiD Destinations created - did_destination_1: " + str(did_destination_1.destination) + " and did_destination_2:  " + str(did_destination_2.destination), order_number, ticket_id)
    # step 4 :  add £1.00 credit in a2billing
    topup_amount =  amount
    buy_topup(account_number, topup_amount, order_number, ticket_id)
    # step 5 :  email and sms customer on completion of the order
    return ('Onboarding Completed Successfully', 200)





def buy_topup(account_number, topup_amount, order_number, ticket_id):
    # ***** test this code for buying topup *****
        account_number = str(account_number)
        credit = topup_amount
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.credit, Card.id).where(Card.username == account_number)
        card = query.execute()

        if not card:
            return Response('Card not found.', 400)
        else:
            #credit = float(request.json['credit'])
            print(card[0].id)
            print(card[0].credit)
            prev_credit = card[0].credit
            new_balance = prev_credit + float(credit)
            Card.update(credit=new_balance).where(Card.username == account_number).execute()
            add_ticket_comment("Top-up Successfull on card with username  " + account_number + " Previous Balance:  " + str(prev_credit) + " New Balance:  " + str(new_balance) , order_number, ticket_id)

            # add logrefill
            logrefill = Logrefill(card=card[0].id, description=account_number, date=str(datetime.datetime.now()), credit=credit, refill_type=0)
            logrefill.save()

            # add logpayment
            logpayment = Logpayment(card=card[0].id, date=str(datetime.datetime.now()), payment=credit, payment_type=0, id_logrefill=logrefill.id)
            logpayment.save()

            # prepare dictionary for JSON return
            data = {
                'account_number': account_number,
                'current_balance': new_balance,
                'credited': credit,
                'datetime': str(datetime.datetime.now()),
                'logrefill_id': logrefill.id,
                'logpayment_id': logpayment.id
            }
        return (data, 200)


def create_a2b_card(data, available_phone_number):
    # ***** test this code for cretaing a card *****
    # using decode() + loads() to convert to dictionary
    req_data = json.loads(data.decode('utf-8'))
    account_number = available_phone_number
    email = req_data['email']
    pin = random.randint(1000,9999)
    passcode = email + str(pin)
    # Create Card
    card = Card.create(username= account_number, useralias= account_number, uipass= passcode, email= email, sip_buddy= 1, lock_pin= pin)
    sipbuddy = SipBuddies.create(username= account_number, accountcode= account_number, name = account_number, secret= passcode, id_cc_card= card.id, context= 'a2billing', regexten= '', callerid= '', fromuser= '', fromdomain= '', host= '', insecure= '', mailbox= '', md5secret= '', deny= '', mask= '', allow= '', musiconhold= '', fullcontact= '', setvar= '')
    result = {'account_number': account_number}
    return jsonify(result)


def create_twilio_subaccount(data):
    # ***** test this code for buying topup *****
    # using decode() + loads() to convert to dictionary
    req_data = json.loads(data.decode('utf-8'))
    account_number = req_data['id']
    account_number = str(account_number)

    # Don't hardcode. Load it from Environment variable.
    account_sid = "Account SID of Master Twilio Account"
    auth_token = "Auth Token of Master Twilio Account"
    client = Client(account_sid, auth_token)

    account = client.api.accounts.create(friendly_name=account_number)


    query = Card.update(company_name = account.sid, company_website = account.auth_token).where(Card.username == account.friendly_name)


    query_result = query.execute()

    result = {'account_sid': account.sid, 'auth_token': account.auth_token, 'friendly_name': account.friendly_name, 'status': account.status}

    if not query_result and not query_result[0]:
            return Response('Card not updated.', 400)
    else:
            return ('Card Updated', 200)


'''
def add_twilio_subaccount_a2bcard(account):

    response_data = account.json()

    sid = response_data['account_sid']
    auth_token = response_data['auth_token']
    account_number = response_data['friendly_name']

    query = Card.update(company_name = sid, company_website = auth_token).where(Card.username == account_number)
    account = query.execute()

    if not account and not account[0]:
            return Response('Card not updated.', 400)
    else:
            return ('Card Updated', 200)
'''


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_data()
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
    print(verified)
    print(type(verified))
    if not verified:
        abort(401)

    # process webhook payload
    # ...

    return ('Webhook verified', 200)




@app.route('/')
def homepage():
    return 'Welcome to Redirect API!'



# New Customer Creation route
@app.route('/v1/customer/create/', methods=['POST'])

def create_customer():
    data = request.get_data()
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    if not verified:
        abort(401)
    else:
        print("Entering else..")
        create_a2b_card(data)
        create_twilio_subaccount(data)
    return ('Customer Account Created', 200)



def add_ticket_comment(message, order_number, ticket_id):
            TicketComment.create(
                                    creator = 2,
                                    creator_type = 1,
                                    date = str(datetime.datetime.now()),
                                    description = message + " for order number: " +str(order_number),
                                    id_ticket = ticket_id
                                )



# Paid Order Processing route
@app.route('/v1/order/paid/', methods=['POST'])

def paid_order():
    #receipt_webhook()

    data = request.get_data()
    header = dict(request.headers)
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    print(verified)
    if not verified:
        abort(404)
    else:
        # using decode() + loads() to convert to dictionary
        req_data = json.loads(data.decode('utf-8'))
        print("Entering else..")
        order_number = req_data['order_number']

        query = Ticket.select(Ticket.id).where(Ticket.title == order_number)
        ticket = query.execute()
        if not ticket:
            new_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 1,
                                    description = "Processing Order number " + str(order_number),
                                    id_component = 5,
                                    priority = 2,
                                    status = 0,
                                    title = str(order_number)
                                    )
        else:
            add_ticket_comment("Webhook Retransmission - Skipping further Processing of Order number ", order_number, ticket[0].id)
            '''
            TicketComment.create(
                                    creator = 2,
                                    creator_type = 1,
                                    date = str(datetime.datetime.now()),
                                    description = "Webhook Retransmission - Skipping further Processing of Order number " + str(order_number),
                                    id_ticket = ticket[0].id
                                )
             '''
            return ('Skipping further processing', 200)
        line_items_list = req_data['line_items']
        email = req_data['email']


        for product_name in line_items_list:
            if 'Top-up' in product_name['name']:
                apply_to_number = product_name['properties']
                if not apply_to_number:
                        print("Topup phone number missing")
                        account_number = '5834639514'
                        add_ticket_comment("Topup phone number missing in the data payload properties", order_number, new_ticket.id)
                else:
                        account_number = apply_to_number[0]
                amount = product_name['price']
                print(account_number, product_name['price'], amount)
                buy_topup(account_number, amount, order_number, new_ticket.id)
            else:
                country = product_name['name']
                email = req_data['email']
                amount = product_name['price']
                forward_to_number = product_name['properties']
                if not forward_to_number:
                        print("Forward to phone number i.e, Destination is missing")
                        destination = '+447412678577'
                        add_ticket_comment("Forward to phone number i.e, Destination is missing in the data payload properties..setting default destination", order_number, new_ticket.id)
                else:
                        destination = forward_to_number[0]

                result = onboarding(country, email, amount, order_number, new_ticket.id, destination)
                print(result)

            Ticket.update(status=1,priority=1).where(Ticket.title == str(order_number)).execute()

    return ('Paid Order fulfilled', 200)



'''
# New Customer Creation route
@app.route('/v1/customer/create/', methods=['POST'])

def create_customer():
    print(request.get_data())
    data = request.get_data()
    print(request.headers.get('X-Shopify-Hmac-SHA256'))
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    if not verified:
        abort(401)
    else:
        print("Entering else..")
        create_a2b_card(data)
        create_twilio_subaccount(data)
    return ('Customer Account Created', 200)

'''




# Order Paid route
@app.route('/paid/<int:account_number>', methods=['POST'])
def paid_order_accnum(account_number):
    data = request.get_data()
    print(request.headers.get('X-Shopify-Hmac-SHA256'))
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    if not verified:
        abort(401)
    else:
    # process webhook payload
        if not request.json or 'credit' not in request.json:
            return Response('Missing credit parameter.', 400)

        account_number = str(account_number)
        # Get Card(vat, credit)
        card = Card.select(Card.credit).where(Card.username == account_number)

        if not card and not card[0]:
            return Response('Card not found.', 400)

        credit = float(request.json['credit'])
        prev_credit = card[0].credit
        new_balance = prev_credit + credit
        Card.update(credit=new_balance).where(Card.username == account_number).execute()


        # add logrefill
        logrefill = Logrefill(card=Card.id, description=account_number, date=str(datetime.datetime.now()), credit=credit, refill_type=0)
        logrefill.save()

        # add logpayment
        logpayment = Logpayment(card=Card.id, date=str(datetime.datetime.now()), payment=credit, payment_type=0, id_logrefill=logrefill.id)
        logpayment.save()

        # prepare dictionary for JSON return
        data = {
            'account_number': account_number,
            'current_balance': new_balance,
            'credited': credit,
            'datetime': str(datetime.datetime.now()),
            'logrefill_id': logrefill.id,
            'logpayment_id': logpayment.id
        }
    return ('Webhook verified', 200)


# @custom_login_required

# Old code - ignor - New Customer Creation route
@app.route('/customer/create/', methods=['POST'])

def create_customer_acc():
    print(request.get_data())
    data = request.get_data()
    print(request.headers.get('X-Shopify-Hmac-SHA256'))
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    if not verified:
        abort(401)
    else:
        # using decode() + loads() to convert to dictionary
        req_data = json.loads(data.decode('utf-8'))
        account_number = req_data['id']
        email = req_data['email']
        print("Entering here********")
        print(account_number)
        print(email)
        # Create Card
        card = Card.create(username= account_number, useralias= account_number, uipass= email, email= email, sip_buddy= 1)

        if not card and not card[0]:
            return Response('Customer account not created.', 400)
    return ('Customer Account Created', 200)


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
