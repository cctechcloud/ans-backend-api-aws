from auth import auth
from app import app
from flask import jsonify
from peewee import *
from functools import wraps
from flask import g, request, redirect, url_for, Response, Flask, abort
import requests, json
from models import Card, Logrefill, Logpayment, Charge, User, Did, DidDestination, CountryServer, SipBuddies, Ticket, TicketComment, Country, Call, VoicemailUsers
import datetime
from flask_cognito import *
import hmac
import hashlib
import base64
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, VoiceResponse, Sip, Gather, Say
import random
import secrets
import os
from app import mail
from flask_mail import Mail, Message
import boto3
from botocore.exceptions import ClientError
from kalyke.client import VoIPClient, APNsClient
from kalyke.payload import PayloadAlert, Payload
import logging
import json, os
from flask import request, Response, render_template, jsonify, Flask
#from pywebpush import webpush, WebPushException




country_code_dict = {"BD": "Bangladesh", "BE": "Belgium", "BF": "Burkina Faso", "BG": "Bulgaria", "BA": "Bosnia and Herzegovina", "BB": "Barbados", "WF": "Wallis and Futuna", "BL": "Saint Barthelemy", "BM": "Bermuda", "BN": "Brunei", "BO": "Bolivia", "BH": "Bahrain", "BI": "Burundi", "BJ": "Benin", "BT": "Bhutan", "JM": "Jamaica", "BV": "Bouvet Island", "BW": "Botswana", "WS": "Samoa", "BQ": "Bonaire, Saint Eustatius and Saba ", "BR": "Brazil", "BS": "Bahamas", "JE": "Jersey", "BY": "Belarus", "BZ": "Belize", "RU": "Russia", "RW": "Rwanda", "RS": "Serbia", "TL": "East Timor", "RE": "Reunion", "TM": "Turkmenistan", "TJ": "Tajikistan", "RO": "Romania", "TK": "Tokelau", "GW": "Guinea-Bissau", "GU": "Guam", "GT": "Guatemala", "GS": "South Georgia and the South Sandwich Islands", "GR": "Greece", "GQ": "Equatorial Guinea", "GP": "Guadeloupe", "JP": "Japan", "GY": "Guyana", "GG": "Guernsey", "GF": "French Guiana", "GE": "Georgia", "GD": "Grenada", "GB": "United Kingdom", "GA": "Gabon", "SV": "El Salvador", "GN": "Guinea", "GM": "Gambia", "GL": "Greenland", "GI": "Gibraltar", "GH": "Ghana", "OM": "Oman", "TN": "Tunisia", "JO": "Jordan", "HR": "Croatia", "HT": "Haiti", "HU": "Hungary", "HK": "Hong Kong", "HN": "Honduras", "HM": "Heard Island and McDonald Islands", "VE": "Venezuela", "PR": "Puerto Rico", "PS": "Palestinian Territory", "PW": "Palau", "PT": "Portugal", "SJ": "Svalbard and Jan Mayen", "PY": "Paraguay", "IQ": "Iraq", "PA": "Panama", "PF": "French Polynesia", "PG": "Papua New Guinea", "PE": "Peru", "PK": "Pakistan", "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland", "PM": "Saint Pierre and Miquelon", "ZM": "Zambia", "EH": "Western Sahara", "EE": "Estonia", "EG": "Egypt", "ZA": "South Africa", "EC": "Ecuador", "IT": "Italy", "VN": "Vietnam", "SB": "Solomon Islands", "ET": "Ethiopia", "SO": "Somalia", "ZW": "Zimbabwe", "SA": "Saudi Arabia", "ES": "Spain", "ER": "Eritrea", "ME": "Montenegro", "MD": "Moldova", "MG": "Madagascar", "MF": "Saint Martin", "MA": "Morocco", "MC": "Monaco", "UZ": "Uzbekistan", "MM": "Myanmar", "ML": "Mali", "MO": "Macao", "MN": "Mongolia", "MH": "Marshall Islands", "MK": "Macedonia", "MU": "Mauritius", "MT": "Malta", "MW": "Malawi", "MV": "Maldives", "MQ": "Martinique", "MP": "Northern Mariana Islands", "MS": "Montserrat", "MR": "Mauritania", "IM": "Isle of Man", "UG": "Uganda", "TZ": "Tanzania", "MY": "Malaysia", "MX": "Mexico", "IL": "Israel", "FR": "France", "IO": "British Indian Ocean Territory", "SH": "Saint Helena", "FI": "Finland", "FJ": "Fiji", "FK": "Falkland Islands", "FM": "Micronesia", "FO": "Faroe Islands", "NI": "Nicaragua", "NL": "Netherlands", "NO": "Norway", "NA": "Namibia", "VU": "Vanuatu", "NC": "New Caledonia", "NE": "Niger", "NF": "Norfolk Island", "NG": "Nigeria", "NZ": "New Zealand", "NP": "Nepal", "NR": "Nauru", "NU": "Niue", "CK": "Cook Islands", "XK": "Kosovo", "CI": "Ivory Coast", "CH": "Switzerland", "CO": "Colombia", "CN": "China", "CM": "Cameroon", "CL": "Chile", "CC": "Cocos Islands", "CA": "Canada", "CG": "Republic of the Congo", "CF": "Central African Republic", "CD": "Democratic Republic of the Congo", "CZ": "Czech Republic", "CY": "Cyprus", "CX": "Christmas Island", "CR": "Costa Rica", "CW": "Curacao", "CV": "Cape Verde", "CU": "Cuba", "SZ": "Swaziland", "SY": "Syria", "SX": "Sint Maarten", "KG": "Kyrgyzstan", "KE": "Kenya", "SS": "South Sudan", "SR": "Suriname", "KI": "Kiribati", "KH": "Cambodia", "KN": "Saint Kitts and Nevis", "KM": "Comoros", "ST": "Sao Tome and Principe", "SK": "Slovakia", "KR": "South Korea", "SI": "Slovenia", "KP": "North Korea", "KW": "Kuwait", "SN": "Senegal", "SM": "San Marino", "SL": "Sierra Leone", "SC": "Seychelles", "KZ": "Kazakhstan", "KY": "Cayman Islands", "SG": "Singapore", "SE": "Sweden", "SD": "Sudan", "DO": "Dominican Republic", "DM": "Dominica", "DJ": "Djibouti", "DK": "Denmark", "VG": "British Virgin Islands", "DE": "Germany", "YE": "Yemen", "DZ": "Algeria", "US": "United States", "UY": "Uruguay", "YT": "Mayotte", "UM": "United States Minor Outlying Islands", "LB": "Lebanon", "LC": "Saint Lucia", "LA": "Laos", "TV": "Tuvalu", "TW": "Taiwan", "TT": "Trinidad and Tobago", "TR": "Turkey", "LK": "Sri Lanka", "LI": "Liechtenstein", "LV": "Latvia", "TO": "Tonga", "LT": "Lithuania", "LU": "Luxembourg", "LR": "Liberia", "LS": "Lesotho", "TH": "Thailand", "TF": "French Southern Territories", "TG": "Togo", "TD": "Chad", "TC": "Turks and Caicos Islands", "LY": "Libya", "VA": "Vatican", "VC": "Saint Vincent and the Grenadines", "AE": "United Arab Emirates", "AD": "Andorra", "AG": "Antigua and Barbuda", "AF": "Afghanistan", "AI": "Anguilla", "VI": "U.S. Virgin Islands", "IS": "Iceland", "IR": "Iran", "AM": "Armenia", "AL": "Albania", "AO": "Angola", "AQ": "Antarctica", "AS": "American Samoa", "AR": "Argentina", "AU": "Australia", "AT": "Austria", "AW": "Aruba", "IN": "India", "AX": "Aland Islands", "AZ": "Azerbaijan", "IE": "Ireland", "ID": "Indonesia", "UA": "Ukraine", "QA": "Qatar", "MZ": "Mozambique"}
inv_country_code_dict = {v: k for k, v in country_code_dict.items()}


ssmclient = boto3.client('ssm')
# Function to retrieve parametsrs from AWS SSM Parameter Store
def get_secret(key):
	resp = ssmclient.get_parameter(
		Name=key,
		WithDecryption=False
	)
	return resp['Parameter']['Value']


#shopify_secret_key = os.environ.get("SHOPIFY_SECRET_KEY")
shopify_secret_key = get_secret('/ans-backend-api/prod/SHOPIFY_SECRET_KEY')
shopify_secret_key = shopify_secret_key.encode()



DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(),"private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(),"public_key.txt")

# VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
# VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

VAPID_CLAIMS = {
"sub": "mailto:grkrishna_mca@yahoo.com"
}

# def send_web_push(subscription_information, message_body):
#     return webpush(
#         subscription_info=subscription_information,
#         data=message_body,
#         vapid_private_key=VAPID_PRIVATE_KEY,
#         vapid_claims=VAPID_CLAIMS
#     )

def send_firebase_push(token):
    #serverToken = os.environ.get("FIREBASE_SERVER_TOKEN")
    serverToken = get_secret('/ans-backend-api/prod/FIREBASE_SERVER_TOKEN')
    deviceToken = token
    pushNotificationTitle = os.environ.get("PUSH_NOTIFICATION_TITLE")
    pushNotificationBody = os.environ.get("PUSH_NOTIFICATION_BODY")
    pushNotificationClickAction = os.environ.get("PUSH_CLICK_ACTION")
    pushNotificationData = os.environ.get("PUSH_NOTIFICATION_DATA")


    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
          }

    body = {
              'notification': {'title': pushNotificationTitle,
                                'body': pushNotificationBody,
                                'click_action': pushNotificationClickAction
                                },
              'to':
                  deviceToken,
              'priority': 'high',
            #   'data': dataPayLoad,
            }
    response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
    print(response.status_code)
    print(response.json())
    return response

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

# function to verify web hook data
def verify_webhook(data, hmac_header):
    print(" **** data from verify_webhook ****")
    digest = hmac.new(shopify_secret_key, data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

# save the subscription in to db -To be implemeneted
@app.route("/v1/adphone/customer/subscription/", methods=["GET", "POST"])
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """

    if request.method == "GET":
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")

    subscription_token = request.get_json("subscription_token")
    return Response(status=201, mimetype="application/json")

# sending the WebPush
@app.route("/v1/adphone/customer/push_v1/",methods=['POST'])
def push_v1():
    message = "Incoming Call from"
    data = request.get_data()
    header = dict(request.headers)
    print(message)
    print(str(data))
    print(str(header))
    # remove the data
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        #req_data = json.loads(data.decode('utf-8'))
        req_data_username = data.decode('utf-8')
        print(req_data_username)
        print("Entering else..")
        device_username = req_data_username
        device_type = 'web'
        #voip_push_token = req_data['sub_token']
        print(device_username)
        print(device_type)
        # Get webpusktoken from SIP Buddies
        sipquery = SipBuddies.select(SipBuddies.username, SipBuddies.setvar).where(SipBuddies.username == device_username)
        sipbuddies = sipquery.execute()

        if not request.json or not request.json.get('username'):
            #return jsonify({'failed':1})
            print("not a json request")

        #token = request.json.get('sub_token')
        token = sipbuddies[0].setvar
        print("token in db is: " + str(token))
        try:
            #token = json.loads(token)
            # send_web_push(token, message)
            send_firebase_push(token)
            return jsonify({'success':1})
        except Exception as e:
            print("error",e)
            return jsonify({'failed':str(e)})


# Registering a new customer
@app.route('/v1/adphone/customer/register/', methods=['POST'])
# ***** function to create free trial user account ******
def customer_registration():
    data = request.get_data()
    header = dict(request.headers)
    # remove the data
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data)
        print(data)
        print(req_data)
        print("Entering else..")
        customer_email = req_data['email']
        email = customer_email
        target_phone = req_data['phone']


        query = Ticket.select(Ticket.id).where(Ticket.title == email)
        ticket = query.execute()
        if not ticket:
            new_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 1,
                                    description = "Adding New Customer " + str(customer_email),
                                    id_component = 5,
                                    priority = 2,
                                    status = 0,
                                    title = str(customer_email)
                                    )
        else:
            add_ticket_comment("Webhook Retransmission - Skipping further Processing of Customer number ", ticket[0].id)
            '''
            TicketComment.create(
                                    creator = 2,
                                    creator_type = 1,
                                    date = str(datetime.datetime.now()),
                                    description = "Webhook Retransmission - Skipping further Processing of Order number " + str(customer_number),
                                    id_ticket = ticket[0].id
                                )
             '''
            print("Webhook Retransmission - Skipping further Processing of Customer number " + str(customer_email) )

            data = {

            }

            message = {
                    'success': 0,
                    'status': 406,
                    'message': 'Email already in use',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        # Check if email already exists
        query = Card.select(Card.username, Card.email, Card.country, Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where(Card.email == customer_email)
        card = query.execute()
        if card:
            data = {

            }

            message = {
                    'success': 0,
                    'status': 406,
                    'message': 'Email already in use',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        # Check if phone already exists
        query = Card.select(Card.username, Card.email, Card.country, Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where(Card.phone == target_phone)
        card = query.execute()
        if card:
            data = {

            }

            message = {
                    'success': 0,
                    'status': 406,
                    'message': 'Phone number already in use',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        customer_number= random.randrange(100000000000,999900000000)
        print(customer_number)
        target_phone = req_data['phone']
        target_phone = target_phone.lstrip('+')
        print(target_phone)

        account_number= target_phone
        #password = req_data['password']
        country = 'GB'
        device_type = req_data['devicetype']
        device_push_token = req_data['devicepushtoken']
        voip_push_token = req_data['voippushtoken']
        # *****  create A2B card for that phone number, create DiD, create DidDestination  ******
        pin = random.randint(1000,9999)
        passcode = req_data['password']
        expiry_date = str(datetime.datetime.now() + datetime.timedelta(30))
        # step 1 : Create Card
        card = Card.create(username= account_number, useralias= account_number, uipass= passcode, email= email, sip_buddy= 1, lock_pin= pin, country= country, expirationdate= expiry_date, enableexpire= '1', phone= target_phone, voicemail_permitted= 1, voicemail_activated= 1, email_notification= email, notify_email= 1, credit_notification= 1)
        sipbuddy = SipBuddies.create(username= target_phone, accountcode= target_phone, name = target_phone, secret= passcode, id_cc_card= Card.id, context= 'a2billing', regexten= '', callerid= target_phone, fromuser= '', fromdomain= '', host= '', insecure= '', mailbox= '', md5secret= '', deny= '', mask= '', allow= '', musiconhold= '', fullcontact= '', usereqphone= device_type, useragent= device_push_token, setvar= voip_push_token)
        # step 2 :  create a DID in a2billing
        did = Did.create(
                            id_cc_didgroup= target_phone,
                            did= target_phone,
                            iduser= Card.id,
                            selling_rate= 0.00,
                            max_concurrent= 2,
                            startingdate= str(datetime.datetime.now()),
                            billingtype= 3,
                            fixrate= 0.00,
                            aleg_carrier_cost_min = 0.00,
                            aleg_carrier_cost_min_offp = 0.00,
                            aleg_carrier_increment = 60,
                            aleg_carrier_increment_offp = 60,
                            aleg_carrier_initblock = 60,
                            aleg_carrier_initblock_offp = 60,
                            aleg_retail_cost_min = 0.00,
                            aleg_retail_cost_min_offp = 0.00,
                            aleg_retail_increment = 60,
                            aleg_retail_increment_offp = 60,
                            aleg_retail_initblock = 60,
                            aleg_retail_initblock_offp = 60
                        )
        # step 3 :  create a DID Destination in a2billing  i.e, sip/linphone destination
        sip_domain = os.environ.get("SIP_DOMAIN")
        sip_proxy = os.environ.get("SIP_PROXY")
        did_destination_1 = DidDestination.create(destination= 'SIP/' + str(target_phone) + '@' + str(sip_domain), priority= 1, id_cc_card= card.id, id_cc_did= did.id, activated= 1, voip_call= 1, validated= 0)

        Ticket.update(status=1,priority=1).where(Ticket.title == str(customer_number)).execute()

        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.username, Card.email, Card.country, Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where(Card.username == account_number)
        card = query.execute()


        # prepare dictionary for JSON return
        data = {
                'account_number': card[0].username,
                'email': card[0].email,
                'phone': card[0].phone,
                'country': card[0].country,
                'datetime': str(datetime.datetime.now()),
                'credit': card[0].credit,
                'first_name': card[0].firstname,
                'last_name': card[0].lastname,
                'id': card[0].id,
                'sip_username': target_phone,
                'sip_secret': passcode,
                'sip_domain': sip_domain,
                'sip_proxy': '',
                'expiry_date': card[0].expirationdate
        }

        message = {
                'success': 1,
                'status': 200,
                'message': 'OK',
                'customer': data
        }

        resp = jsonify(message)
        resp.status_code = 200
        resp.mimetype = 'application/json'
        print(resp)
        return resp


# Update Web Push token in database
@app.route('/v1/adphone/customer/webpushtoken/', methods=['POST'])
# ***** function to create free trial user account ******
def customer_webpushtoken():
    data = request.get_data()
    header = dict(request.headers)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        device_username = req_data['user']['username']
        device_type = 'web'
        voip_push_token = req_data['user']['subtoken']
        print(device_username)
        print(device_type)
        print(voip_push_token)
        # Update device info and push tokens
        SipBuddies.update(usereqphone=device_type, setvar=voip_push_token).where(SipBuddies.username == device_username).execute()
        message = {
                        'success': 1,
                        'status': 200,
                        'message': 'webpushtoken saved'
        }

        resp = jsonify(message)
        resp.status_code = 200
        resp.mimetype = 'application/json'
        return resp

# Customer Login
@app.route('/v1/adphone/customer/login/', methods=['POST'])
# ***** function to create free trial user account ******
def customer_login():
    data = request.get_data()
    header = dict(request.headers)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        customer_email = req_data['email']
        customer_password = req_data['password']
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.id).where((Card.email == customer_email) & (Card.uipass == customer_password))
        card = query.execute()

        if not card:
            data = {

            }

            message = {
                    'success': 0,
                    'status': 401,
                    'message': 'Invalid Login Details',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        else:
            query = Card.select(Card.id, Card.credit, Card.firstname, Card.lastname, Card.phone, Card.username, Card.phone, Card.email, Card.useralias).where((Card.email == customer_email) & (Card.uipass == customer_password))
            card = query.execute()
            print(card[0].id)
            length = 15
            id_token_string = str(secrets.token_hex(16)[0:length])
            Card.update(useralias=id_token_string).where(Card.username == card[0].username).execute()

            sip_domain = os.environ.get("SIP_DOMAIN")
            sip_proxy = os.environ.get("SIP_PROXY")
            print(sip_domain)
            print(sip_proxy)

            # device_type = req_data['devicetype']
            # device_push_token = req_data['devicepushtoken']
            # voip_push_token = req_data['voippushtoken']
            device_username = req_data['username']
            device_type = 'web'
            device_push_token= ''
            voip_push_token = req_data['sub_token']


            # Update device info and push tokens
            SipBuddies.update(usereqphone=device_type, useragent=device_push_token, setvar=voip_push_token).where(SipBuddies.username == card[0].phone).execute()

            # Get SIP account details
            sipquery = SipBuddies.select(SipBuddies.username, SipBuddies.secret).where(SipBuddies.username == card[0].phone)
            print(str(sipquery))
            sipbuddies = sipquery.execute()
            print(sipbuddies)


            # prepare dictionary for JSON return
            data = {
                'account_number': card[0].username,
                'current_balance': card[0].credit,
                'email': card[0].email,
                'phone': card[0].phone,
                'first_name': card[0].firstname,
                'last_name': card[0].lastname,
                'country': card[0].country,
                'id_token': id_token_string,
                'sip_username': sipbuddies[0].username,
                'sip_secret': sipbuddies[0].secret,
                'sip_domain': sip_domain,
                'sip_proxy': sip_proxy,
                'expiry_date': card[0].expirationdate
            }

            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'Logged in',
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp


# Add credit to existing customer
@app.route('/v1/adphone/credit/add/', methods=['POST'])
def add_credit():
    data = request.get_data()
    header = dict(request.headers)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        id_token = req_data['id_token']
        account_number = req_data['account_number']
        credit_amount = req_data['credit_amount']

    # ***** test this code for buying topup *****
        account_number = str(account_number)
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where((Card.useralias == id_token) & (Card.username == account_number))
        print(query)
        card = query.execute()

        if not card:

            customer_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 0,
                                    description = "Add Credit issue - card not found. check in A2B - card # " + str(account_number),
                                    id_component = 7,
                                    priority = 3,
                                    status = 0,
                                    title = "Add Credit issue - " + str(account_number)
                                    )
            data = {

            }

            message = {
                    'success': 0,
                    'status': 406,
                    'message': 'Card not found',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp
        else:
            #credit = float(request.json['credit'])
            print(card[0].id)
            print(card[0].credit)
            print(card[0].phone)
            prev_credit = card[0].credit
            new_balance = prev_credit + float(credit_amount)
            firstname = card[0].firstname
            lastname = card[0].lastname
            phone = card[0].phone
            Card.update(credit=new_balance).where(Card.username == account_number).execute()


            # add logrefill
            logrefill = Logrefill(card=card[0].id, description=account_number, date=str(datetime.datetime.now()), credit=credit_amount, refill_type=0)
            logrefill.save()

            # add logpayment
            logpayment = Logpayment(card=card[0].id, date=str(datetime.datetime.now()), payment=credit_amount, payment_type=0, id_logrefill=logrefill.id)
            logpayment.save()

            # prepare dictionary for JSON return
            data = {
                'account_number': account_number,
                'current_balance': new_balance,
                'credited': credit_amount,
                'datetime': str(datetime.datetime.now()),
                'logrefill_id': logrefill.id,
                'logpayment_id': logpayment.id
            }
            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'Credit Updated',
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            print(resp.mimetype)
            return resp





# Change Password - Send OTP
@app.route('/v1/adphone/customer/changepassword/sendauth', methods=['POST'])
# ***** function to create free trial user account ******
def cp_send_auth():
    data = request.get_data()
    header = dict(request.headers)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        customer_email = req_data['email']
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.id).where(Card.email == customer_email)
        card = query.execute()

        if not card:
            data = {

            }

            message = {
                    'success': 0,
                    'status': 401,
                    'message': 'Email address not registered',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        else:
            query = Card.select(Card.id, Card.lock_pin, Card.email).where(Card.email == customer_email)
            card = query.execute()
            print(card[0].id)
            lock_pin = random.randrange(100000,999999)
            lock_pin_string = str(lock_pin)
            Card.update(lock_pin=lock_pin_string).where(Card.email == customer_email).execute()

            email_subject = 'One Time Password (OTP) for Change Password.'
            email_body_text = '''Dear Customer,
                            {} - Use this OTP to change your password for accessing your account. Regards, Team Adphone'''.format(lock_pin_string)
            email_body_html = '''<html>
                             <head></head>
                             <body>
                               <p>Dear Customer,</p> <h3>Your One Time Password (OTP) : {} </h3>
                               <p>Use this OTP to change your password for accessing your account.</p>
                               <p>Regards,</p>
                               <p> Team Adphone</p>
                            </body>
                            </html>'''.format(lock_pin_string)
            send_email(customer_email, email_subject, email_body_text, email_body_html)

            # prepare dictionary for JSON return
            data = {
                'email': card[0].email,
            }

            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'OTP sent to email address : ' + str(card[0].email),
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp


# Change Password - Validate OTP
@app.route('/v1/adphone/customer/changepassword/validateauth', methods=['POST'])
# ***** function to create free trial user account ******
def cp_validate_auth():
    data = request.get_data()
    header = dict(request.headers)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        customer_email = req_data['email']
        customer_otp= req_data['otp']
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.id).where((Card.email == customer_email) & (Card.lock_pin == customer_otp))
        card = query.execute()

        if not card:
            data = {

            }

            message = {
                    'success': 0,
                    'status': 401,
                    'message': 'OTP is invalid or expired',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        else:
            query = Card.select(Card.id, Card.username, Card.email).where((Card.email == customer_email) & (Card.lock_pin == customer_otp))
            card = query.execute()
            print(card[0].id)
            # prepare dictionary for JSON return
            data = {
                'account_number': card[0].username,
                'email': card[0].email,
                'id': card[0].id,
            }

            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'OTP validated successfully',
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp



# Change Password - New password
@app.route('/v1/adphone/customer/changepassword/update', methods=['POST'])
# ***** function to create free trial user account ******
def cp_update_password():
    data = request.get_data()
    header = dict(request.headers)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        customer_email = req_data['email']
        account_number = req_data['account_number']
        new_password = req_data['new_password']
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.id).where((Card.email == customer_email) & (Card.username == account_number))
        card = query.execute()

        if not card:
            data = {

            }

            message = {
                    'success': 0,
                    'status': 401,
                    'message': 'Card not present',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

        else:
            current_password = card[0].uipass

            Card.update(uipass=new_password).where((Card.username == account_number) & (Card.email == customer_email)).execute()


            # prepare dictionary for JSON return
            data = {

            }

            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'Password changed successfully',
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp

# Send VOIP Push Notification to APNS
@app.route('/v1/adphone/push/voip/ios', methods=['GET', 'POST'])
def push_voip_ios():
    data = request.get_data()
    sip_user = data.decode('utf-8')
    print("sip user is: " + sip_user)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        print("Ready to Send VOIP Push")
        client = VoIPClient(
        auth_key_filepath='./VOIP.pem',
        bundle_id='cctech.RoamFree.voip', use_sandbox=True
        )

        alert = {
             'msg': 'Incoming Call'
        }
        # Get SIP account details
        sipquery = SipBuddies.select(SipBuddies.username, SipBuddies.usereqphone, SipBuddies.setvar, SipBuddies.useragent).where(SipBuddies.username == sip_user)
        sipbuddies = sipquery.execute()
        # Send single VoIP notification
        voip_push_token = sipbuddies[0].setvar
        result = client.send_message(voip_push_token, alert)
        print("VOIP Push result is: " + str(result))
        # Send multiple VoIP notifications
        #registration_ids = [
        #    '84b7120bf190d171ff904bc943455d6081274714b32cfa28814be7ee921fb', 'afaa8dcedc99d420e35f7ad3c8c7d5071b2697da9bd7a5037ad'
        #]
        #results = client.send_bulk_message(registration_ids, alert)
        return str(result)

# Send Regular Push Notification to APNS
@app.route('/v1/adphone/push/ios/notification', methods=['GET', 'POST'])
def push_ios_notification():
    data = request.get_data()
    sip_user = data.decode('utf-8')
    print("sip user is: " + sip_user)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        print("Ready to Send Standard IOS Push")
        payload_alert = PayloadAlert(title='MSG From RoamFree', body='It is time to free recharge to continue using our service.')
        alert = Payload(alert=payload_alert, badge=1, sound='default')
        client = APNsClient(
            team_id='3RG7H65HWR', auth_key_id='8Z2CD246V6', auth_key_filepath='./AuthKey_8Z2CD246V6.p8',
            bundle_id='cctech.RoamFree', use_sandbox=True, force_proto='h2'
        )
        # Get SIP account details
        sipquery = SipBuddies.select(SipBuddies.username, SipBuddies.usereqphone, SipBuddies.setvar, SipBuddies.useragent).where(SipBuddies.username == sip_user)
        sipbuddies = sipquery.execute()
        # Send single Standad IOS notification
        device_push_token = sipbuddies[0].useragent
        print(device_push_token)
        result = client.send_message(device_push_token, alert)
        print("IOS Push result is: " + str(result))
        # Send multiple push notifications
        #registration_ids = [
        #    '87b0a5ab7b91dce26ea2c97466f7b3b82b5dda4441003a2d8782fffd76515b73', '22a1b20cb67a43da4a8f006176788aa20271ac2e3ac0da0375ae3dc1db0de210'
        #]
        #results = client.send_bulk_message(registration_ids, alert)
        return str(result)

# Home page route for site status
@app.route('/v1/adphone/countries/getall', methods=['GET', 'POST'])
def countries_getall():

    country_dial_code_dict = {"success":1,"data":[{"countryName":"Afghanistan","countryCode":"AF","dialCode":"+93","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c3","flag":"uploads/flags/flags/af.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.580Z","updatedDateTime":"2020-04-01T16:04:53.580Z"},{"countryName":"Albania","countryCode":"AL","dialCode":"+355","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c4","flag":"uploads/flags/flags/al.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"Algeria","countryCode":"DZ","dialCode":"+213","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c5","flag":"uploads/flags/flags/dz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"AmericanSamoa","countryCode":"AS","dialCode":"+1684","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c6","flag":"uploads/flags/flags/as.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"Andorra","countryCode":"AD","dialCode":"+376","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c7","flag":"uploads/flags/flags/ad.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"Angola","countryCode":"AO","dialCode":"+244","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c8","flag":"uploads/flags/flags/ao.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"Anguilla","countryCode":"AI","dialCode":"+1 264","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c9","flag":"uploads/flags/flags/ai.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"Antigua and Barbuda","countryCode":"AG","dialCode":"+1268","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ca","flag":"uploads/flags/flags/ag.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.581Z","updatedDateTime":"2020-04-01T16:04:53.581Z"},{"countryName":"Argentina","countryCode":"AR","dialCode":"+54","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078cb","flag":"uploads/flags/flags/ar.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.582Z","updatedDateTime":"2020-04-01T16:04:53.582Z"},{"countryName":"Armenia","countryCode":"AM","dialCode":"+374","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078cc","flag":"uploads/flags/flags/am.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.582Z","updatedDateTime":"2020-04-01T16:04:53.582Z"},{"countryName":"Aruba","countryCode":"AW","dialCode":"+297","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078cd","flag":"uploads/flags/flags/aw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.582Z","updatedDateTime":"2020-04-01T16:04:53.582Z"},{"countryName":"Australia","countryCode":"AU","dialCode":"+61","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ce","flag":"uploads/flags/flags/au.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.582Z","updatedDateTime":"2020-04-01T16:04:53.582Z"},{"countryName":"Austria","countryCode":"AT","dialCode":"+43","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078cf","flag":"uploads/flags/flags/at.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.582Z","updatedDateTime":"2020-04-01T16:04:53.582Z"},{"countryName":"Azerbaijan","countryCode":"AZ","dialCode":"+994","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d0","flag":"uploads/flags/flags/az.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.582Z","updatedDateTime":"2020-04-01T16:04:53.582Z"},{"countryName":"Bahamas","countryCode":"BS","dialCode":"+1 242","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d1","flag":"uploads/flags/flags/bs.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Bahrain","countryCode":"BH","dialCode":"+973","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d2","flag":"uploads/flags/flags/bh.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Bangladesh","countryCode":"BD","dialCode":"+880","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d3","flag":"uploads/flags/flags/bd.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Barbados","countryCode":"BB","dialCode":"+1 246","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d4","flag":"uploads/flags/flags/bb.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Belarus","countryCode":"BY","dialCode":"+375","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d5","flag":"uploads/flags/flags/by.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Belgium","countryCode":"BE","dialCode":"+32","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d6","flag":"uploads/flags/flags/be.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Belize","countryCode":"BZ","dialCode":"+501","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d7","flag":"uploads/flags/flags/bz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Benin","countryCode":"BJ","dialCode":"+229","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d8","flag":"uploads/flags/flags/bj.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.583Z","updatedDateTime":"2020-04-01T16:04:53.583Z"},{"countryName":"Bermuda","countryCode":"BM","dialCode":"+1 441","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078d9","flag":"uploads/flags/flags/bm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Bhutan","countryCode":"BT","dialCode":"+975","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078da","flag":"uploads/flags/flags/bt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Bolivia, Plurinational State of","countryCode":"BO","dialCode":"+591","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907989","flag":"uploads/flags/flags/bo.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Bosnia and Herzegovina","countryCode":"BA","dialCode":"+387","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078db","flag":"uploads/flags/flags/ba.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Botswana","countryCode":"BW","dialCode":"+267","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078dc","flag":"uploads/flags/flags/bw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Brazil","countryCode":"BR","dialCode":"+55","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078dd","flag":"uploads/flags/flags/br.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"British Indian Ocean Territory","countryCode":"IO","dialCode":"+246","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078de","flag":"uploads/flags/flags/io.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Brunei Darussalam","countryCode":"BN","dialCode":"+673","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090798a","flag":"uploads/flags/flags/bn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.584Z","updatedDateTime":"2020-04-01T16:04:53.584Z"},{"countryName":"Bulgaria","countryCode":"BG","dialCode":"+359","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078df","flag":"uploads/flags/flags/bg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Burkina Faso","countryCode":"BF","dialCode":"+226","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e0","flag":"uploads/flags/flags/bf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Burundi","countryCode":"BI","dialCode":"+257","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e1","flag":"uploads/flags/flags/bi.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Cambodia","countryCode":"KH","dialCode":"+855","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e2","flag":"uploads/flags/flags/kh.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Cameroon","countryCode":"CM","dialCode":"+237","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e3","flag":"uploads/flags/flags/cm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Canada","countryCode":"CA","dialCode":"+1","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e4","flag":"uploads/flags/flags/ca.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Cape Verde","countryCode":"CV","dialCode":"+238","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e5","flag":"uploads/flags/flags/cv.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Cayman Islands","countryCode":"KY","dialCode":"+ 345","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e6","flag":"uploads/flags/flags/ky.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Central African Republic","countryCode":"CF","dialCode":"+236","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e7","flag":"uploads/flags/flags/cf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.585Z","updatedDateTime":"2020-04-01T16:04:53.585Z"},{"countryName":"Chad","countryCode":"TD","dialCode":"+235","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e8","flag":"uploads/flags/flags/td.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.586Z","updatedDateTime":"2020-04-01T16:04:53.586Z"},{"countryName":"Chile","countryCode":"CL","dialCode":"+56","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078e9","flag":"uploads/flags/flags/cl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.586Z","updatedDateTime":"2020-04-01T16:04:53.586Z"},{"countryName":"China","countryCode":"CN","dialCode":"+86","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ea","flag":"uploads/flags/flags/cn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.586Z","updatedDateTime":"2020-04-01T16:04:53.586Z"},{"countryName":"Christmas Island","countryCode":"CX","dialCode":"+61","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078eb","flag":"uploads/flags/flags/cx.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.586Z","updatedDateTime":"2020-04-01T16:04:53.586Z"},{"countryName":"Cocos (Keeling) Islands","countryCode":"CC","dialCode":"+61","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090798b","flag":"uploads/flags/flags/cc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.587Z","updatedDateTime":"2020-04-01T16:04:53.587Z"},{"countryName":"Colombia","countryCode":"CO","dialCode":"+57","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ec","flag":"uploads/flags/flags/co.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Comoros","countryCode":"KM","dialCode":"+269","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ed","flag":"uploads/flags/flags/km.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Congo","countryCode":"CG","dialCode":"+242","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ee","flag":"uploads/flags/flags/cg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Congo, The Democratic Republic of the","countryCode":"CD","dialCode":"+243","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090798c","flag":"uploads/flags/flags/cd.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Cook Islands","countryCode":"CK","dialCode":"+682","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ef","flag":"uploads/flags/flags/ck.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Costa Rica","countryCode":"CR","dialCode":"+506","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f0","flag":"uploads/flags/flags/cr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Cote d'Ivoire","countryCode":"CI","dialCode":"+225","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090798d","flag":"uploads/flags/flags/ci.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Croatia","countryCode":"HR","dialCode":"+385","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f1","flag":"uploads/flags/flags/hr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.588Z","updatedDateTime":"2020-04-01T16:04:53.588Z"},{"countryName":"Cuba","countryCode":"CU","dialCode":"+53","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f2","flag":"uploads/flags/flags/cu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Cyprus","countryCode":"CY","dialCode":"+537","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f3","flag":"uploads/flags/flags/cy.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Czech Republic","countryCode":"CZ","dialCode":"+420","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f4","flag":"uploads/flags/flags/cz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Denmark","countryCode":"DK","dialCode":"+45","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f5","flag":"uploads/flags/flags/dk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Djibouti","countryCode":"DJ","dialCode":"+253","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f6","flag":"uploads/flags/flags/dj.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Dominica","countryCode":"DM","dialCode":"+1 767","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f7","flag":"uploads/flags/flags/dm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Dominican Republic","countryCode":"DO","dialCode":"+1 849","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f8","flag":"uploads/flags/flags/do.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Ecuador","countryCode":"EC","dialCode":"+593","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078f9","flag":"uploads/flags/flags/ec.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"Egypt","countryCode":"EG","dialCode":"+20","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078fa","flag":"uploads/flags/flags/eg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.589Z","updatedDateTime":"2020-04-01T16:04:53.589Z"},{"countryName":"El Salvador","countryCode":"SV","dialCode":"+503","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078fb","flag":"uploads/flags/flags/sv.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Equatorial Guinea","countryCode":"GQ","dialCode":"+240","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078fc","flag":"uploads/flags/flags/gq.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Eritrea","countryCode":"ER","dialCode":"+291","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078fd","flag":"uploads/flags/flags/er.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Estonia","countryCode":"EE","dialCode":"+372","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078fe","flag":"uploads/flags/flags/ee.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Ethiopia","countryCode":"ET","dialCode":"+251","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078ff","flag":"uploads/flags/flags/et.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Falkland Islands (Malvinas)","countryCode":"FK","dialCode":"+500","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090798e","flag":"uploads/flags/flags/fk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Faroe Islands","countryCode":"FO","dialCode":"+298","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907900","flag":"uploads/flags/flags/fo.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.590Z","updatedDateTime":"2020-04-01T16:04:53.590Z"},{"countryName":"Fiji","countryCode":"FJ","dialCode":"+679","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907901","flag":"uploads/flags/flags/fj.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"Finland","countryCode":"FI","dialCode":"+358","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907902","flag":"uploads/flags/flags/fi.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"France","countryCode":"FR","dialCode":"+33","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907903","flag":"uploads/flags/flags/fr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"French Guiana","countryCode":"GF","dialCode":"+594","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907904","flag":"uploads/flags/flags/gf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"French Polynesia","countryCode":"PF","dialCode":"+689","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907905","flag":"uploads/flags/flags/pf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"Gabon","countryCode":"GA","dialCode":"+241","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907906","flag":"uploads/flags/flags/ga.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"Gambia","countryCode":"GM","dialCode":"+220","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907907","flag":"uploads/flags/flags/gm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"Georgia","countryCode":"GE","dialCode":"+995","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907908","flag":"uploads/flags/flags/ge.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"Germany","countryCode":"DE","dialCode":"+49","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907909","flag":"uploads/flags/flags/de.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.591Z","updatedDateTime":"2020-04-01T16:04:53.591Z"},{"countryName":"Ghana","countryCode":"GH","dialCode":"+233","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090790a","flag":"uploads/flags/flags/gh.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.592Z","updatedDateTime":"2020-04-01T16:04:53.592Z"},{"countryName":"Gibraltar","countryCode":"GI","dialCode":"+350","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090790b","flag":"uploads/flags/flags/gi.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.592Z","updatedDateTime":"2020-04-01T16:04:53.592Z"},{"countryName":"Greece","countryCode":"GR","dialCode":"+30","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090790c","flag":"uploads/flags/flags/gr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.592Z","updatedDateTime":"2020-04-01T16:04:53.592Z"},{"countryName":"Greenland","countryCode":"GL","dialCode":"+299","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090790d","flag":"uploads/flags/flags/gl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.592Z","updatedDateTime":"2020-04-01T16:04:53.592Z"},{"countryName":"Grenada","countryCode":"GD","dialCode":"+1 473","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090790e","flag":"uploads/flags/flags/gd.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.592Z","updatedDateTime":"2020-04-01T16:04:53.592Z"},{"countryName":"Guadeloupe","countryCode":"GP","dialCode":"+590","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090790f","flag":"uploads/flags/flags/gp.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.592Z","updatedDateTime":"2020-04-01T16:04:53.592Z"},{"countryName":"Guam","countryCode":"GU","dialCode":"+1 671","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907910","flag":"uploads/flags/flags/gu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.595Z","updatedDateTime":"2020-04-01T16:04:53.595Z"},{"countryName":"Guatemala","countryCode":"GT","dialCode":"+502","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907911","flag":"uploads/flags/flags/gt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.595Z","updatedDateTime":"2020-04-01T16:04:53.595Z"},{"countryName":"Guernsey","countryCode":"GG","dialCode":"+44","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090798f","flag":"uploads/flags/flags/gg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.596Z","updatedDateTime":"2020-04-01T16:04:53.596Z"},{"countryName":"Guinea","countryCode":"GN","dialCode":"+224","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907912","flag":"uploads/flags/flags/gn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.596Z","updatedDateTime":"2020-04-01T16:04:53.596Z"},{"countryName":"Guinea-Bissau","countryCode":"GW","dialCode":"+245","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907913","flag":"uploads/flags/flags/gw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.596Z","updatedDateTime":"2020-04-01T16:04:53.596Z"},{"countryName":"Guyana","countryCode":"GY","dialCode":"+595","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907914","flag":"uploads/flags/flags/gy.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.596Z","updatedDateTime":"2020-04-01T16:04:53.596Z"},{"countryName":"Haiti","countryCode":"HT","dialCode":"+509","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907915","flag":"uploads/flags/flags/ht.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.596Z","updatedDateTime":"2020-04-01T16:04:53.596Z"},{"countryName":"Holy See (Vatican City State)","countryCode":"VA","dialCode":"+379","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907990","flag":"uploads/flags/flags/va.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.596Z","updatedDateTime":"2020-04-01T16:04:53.596Z"},{"countryName":"Honduras","countryCode":"HN","dialCode":"+504","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907916","flag":"uploads/flags/flags/hn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Hong Kong","countryCode":"HK","dialCode":"+852","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907991","flag":"uploads/flags/flags/hk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Hungary","countryCode":"HU","dialCode":"+36","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907917","flag":"uploads/flags/flags/hu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Iceland","countryCode":"IS","dialCode":"+354","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907918","flag":"uploads/flags/flags/is.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"India","countryCode":"IN","dialCode":"+91","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907919","flag":"uploads/flags/flags/in.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Indonesia","countryCode":"ID","dialCode":"+62","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090791a","flag":"uploads/flags/flags/id.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Iran, Islamic Republic of","countryCode":"IR","dialCode":"+98","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907992","flag":"uploads/flags/flags/ir.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Iraq","countryCode":"IQ","dialCode":"+964","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090791b","flag":"uploads/flags/flags/iq.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Ireland","countryCode":"IE","dialCode":"+353","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090791c","flag":"uploads/flags/flags/ie.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.598Z","updatedDateTime":"2020-04-01T16:04:53.598Z"},{"countryName":"Isle of Man","countryCode":"IM","dialCode":"+44","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907993","flag":"uploads/flags/flags/im.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Israel","countryCode":"IL","dialCode":"+972","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109078c2","flag":"uploads/flags/flags/il.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Israel","countryCode":"IL","dialCode":"+972","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090791d","flag":"uploads/flags/flags/il.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Italy","countryCode":"IT","dialCode":"+39","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090791e","flag":"uploads/flags/flags/it.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Jamaica","countryCode":"JM","dialCode":"+1 876","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090791f","flag":"uploads/flags/flags/jm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Japan","countryCode":"JP","dialCode":"+81","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907920","flag":"uploads/flags/flags/jp.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Jersey","countryCode":"JE","dialCode":"+44","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907994","flag":"uploads/flags/flags/je.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Jordan","countryCode":"JO","dialCode":"+962","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907921","flag":"uploads/flags/flags/jo.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.599Z","updatedDateTime":"2020-04-01T16:04:53.599Z"},{"countryName":"Kazakhstan","countryCode":"KZ","dialCode":"+7 7","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907922","flag":"uploads/flags/flags/kz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Kenya","countryCode":"KE","dialCode":"+254","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907923","flag":"uploads/flags/flags/ke.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Kiribati","countryCode":"KI","dialCode":"+686","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907924","flag":"uploads/flags/flags/ki.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Korea, Democratic People's Republic of","countryCode":"KP","dialCode":"+850","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907995","flag":"uploads/flags/flags/kp.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Korea, Republic of","countryCode":"KR","dialCode":"+82","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907996","flag":"uploads/flags/flags/kr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Kuwait","countryCode":"KW","dialCode":"+965","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907925","flag":"uploads/flags/flags/kw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Kyrgyzstan","countryCode":"KG","dialCode":"+996","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907926","flag":"uploads/flags/flags/kg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Lao People's Democratic Republic","countryCode":"LA","dialCode":"+856","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907997","flag":"uploads/flags/flags/la.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.600Z","updatedDateTime":"2020-04-01T16:04:53.600Z"},{"countryName":"Latvia","countryCode":"LV","dialCode":"+371","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907927","flag":"uploads/flags/flags/lv.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Lebanon","countryCode":"LB","dialCode":"+961","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907928","flag":"uploads/flags/flags/lb.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Lesotho","countryCode":"LS","dialCode":"+266","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907929","flag":"uploads/flags/flags/ls.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Liberia","countryCode":"LR","dialCode":"+231","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090792a","flag":"uploads/flags/flags/lr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Libyan Arab Jamahiriya","countryCode":"LY","dialCode":"+218","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907998","flag":"uploads/flags/flags/ly.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Liechtenstein","countryCode":"LI","dialCode":"+423","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090792b","flag":"uploads/flags/flags/li.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Lithuania","countryCode":"LT","dialCode":"+370","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090792c","flag":"uploads/flags/flags/lt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Luxembourg","countryCode":"LU","dialCode":"+352","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090792d","flag":"uploads/flags/flags/lu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.601Z","updatedDateTime":"2020-04-01T16:04:53.601Z"},{"countryName":"Macao","countryCode":"MO","dialCode":"+853","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907999","flag":"uploads/flags/flags/mo.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Macedonia, The Former Yugoslav Republic of","countryCode":"MK","dialCode":"+389","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090799a","flag":"uploads/flags/flags/mk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Madagascar","countryCode":"MG","dialCode":"+261","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090792e","flag":"uploads/flags/flags/mg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Malawi","countryCode":"MW","dialCode":"+265","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090792f","flag":"uploads/flags/flags/mw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Malaysia","countryCode":"MY","dialCode":"+60","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907930","flag":"uploads/flags/flags/my.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Maldives","countryCode":"MV","dialCode":"+960","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907931","flag":"uploads/flags/flags/mv.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Mali","countryCode":"ML","dialCode":"+223","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907932","flag":"uploads/flags/flags/ml.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Malta","countryCode":"MT","dialCode":"+356","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907933","flag":"uploads/flags/flags/mt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Marshall Islands","countryCode":"MH","dialCode":"+692","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907934","flag":"uploads/flags/flags/mh.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.602Z","updatedDateTime":"2020-04-01T16:04:53.602Z"},{"countryName":"Martinique","countryCode":"MQ","dialCode":"+596","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907935","flag":"uploads/flags/flags/mq.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Mauritania","countryCode":"MR","dialCode":"+222","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907936","flag":"uploads/flags/flags/mr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Mauritius","countryCode":"MU","dialCode":"+230","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907937","flag":"uploads/flags/flags/mu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Mayotte","countryCode":"YT","dialCode":"+262","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907938","flag":"uploads/flags/flags/yt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Mexico","countryCode":"MX","dialCode":"+52","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907939","flag":"uploads/flags/flags/mx.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Micronesia, Federated States of","countryCode":"FM","dialCode":"+691","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090799b","flag":"uploads/flags/flags/fm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Moldova, Republic of","countryCode":"MD","dialCode":"+373","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090799c","flag":"uploads/flags/flags/md.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Monaco","countryCode":"MC","dialCode":"+377","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090793a","flag":"uploads/flags/flags/mc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.603Z","updatedDateTime":"2020-04-01T16:04:53.603Z"},{"countryName":"Mongolia","countryCode":"MN","dialCode":"+976","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090793b","flag":"uploads/flags/flags/mn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Montenegro","countryCode":"ME","dialCode":"+382","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090793c","flag":"uploads/flags/flags/me.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Montserrat","countryCode":"MS","dialCode":"+1664","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090793d","flag":"uploads/flags/flags/ms.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Morocco","countryCode":"MA","dialCode":"+212","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090793e","flag":"uploads/flags/flags/ma.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Mozambique","countryCode":"MZ","dialCode":"+258","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090799d","flag":"uploads/flags/flags/mz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Myanmar","countryCode":"MM","dialCode":"+95","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090793f","flag":"uploads/flags/flags/mm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Namibia","countryCode":"NA","dialCode":"+264","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907940","flag":"uploads/flags/flags/na.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.604Z","updatedDateTime":"2020-04-01T16:04:53.604Z"},{"countryName":"Nauru","countryCode":"NR","dialCode":"+674","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907941","flag":"uploads/flags/flags/nr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.605Z","updatedDateTime":"2020-04-01T16:04:53.605Z"},{"countryName":"Nepal","countryCode":"NP","dialCode":"+977","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907942","flag":"uploads/flags/flags/np.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"Netherlands","countryCode":"NL","dialCode":"+31","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907943","flag":"uploads/flags/flags/nl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"Netherlands Antilles","countryCode":"AN","dialCode":"+599","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907944","flag":"uploads/flags/flags/an.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"New Caledonia","countryCode":"NC","dialCode":"+687","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907945","flag":"uploads/flags/flags/nc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"New Zealand","countryCode":"NZ","dialCode":"+64","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907946","flag":"uploads/flags/flags/nz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"Nicaragua","countryCode":"NI","dialCode":"+505","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907947","flag":"uploads/flags/flags/ni.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"Niger","countryCode":"NE","dialCode":"+227","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907948","flag":"uploads/flags/flags/ne.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"Nigeria","countryCode":"NG","dialCode":"+234","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907949","flag":"uploads/flags/flags/ng.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.606Z","updatedDateTime":"2020-04-01T16:04:53.606Z"},{"countryName":"Niue","countryCode":"NU","dialCode":"+683","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090794a","flag":"uploads/flags/flags/nu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Norfolk Island","countryCode":"NF","dialCode":"+672","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090794b","flag":"uploads/flags/flags/nf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Northern Mariana Islands","countryCode":"MP","dialCode":"+1 670","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090794c","flag":"uploads/flags/flags/mp.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Norway","countryCode":"NO","dialCode":"+47","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090794d","flag":"uploads/flags/flags/no.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Oman","countryCode":"OM","dialCode":"+968","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090794e","flag":"uploads/flags/flags/om.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Pakistan","countryCode":"PK","dialCode":"+92","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090794f","flag":"uploads/flags/flags/pk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Palau","countryCode":"PW","dialCode":"+680","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907950","flag":"uploads/flags/flags/pw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Palestinian Territory, Occupied","countryCode":"PS","dialCode":"+970","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090799e","flag":"uploads/flags/flags/ps.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.607Z"},{"countryName":"Panama","countryCode":"PA","dialCode":"+507","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907951","flag":"uploads/flags/flags/pa.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.607Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Papua New Guinea","countryCode":"PG","dialCode":"+675","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907952","flag":"uploads/flags/flags/pg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.608Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Paraguay","countryCode":"PY","dialCode":"+595","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907953","flag":"uploads/flags/flags/py.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.608Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Peru","countryCode":"PE","dialCode":"+51","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907954","flag":"uploads/flags/flags/pe.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.608Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Philippines","countryCode":"PH","dialCode":"+63","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907955","flag":"uploads/flags/flags/ph.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.608Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Pitcairn","countryCode":"PN","dialCode":"+872","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090799f","flag":"uploads/flags/flags/pn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.608Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Poland","countryCode":"PL","dialCode":"+48","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907956","flag":"uploads/flags/flags/pl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.608Z","updatedDateTime":"2020-04-01T16:04:53.608Z"},{"countryName":"Portugal","countryCode":"PT","dialCode":"+351","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907957","flag":"uploads/flags/flags/pt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Puerto Rico","countryCode":"PR","dialCode":"+1 939","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907958","flag":"uploads/flags/flags/pr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Qatar","countryCode":"QA","dialCode":"+974","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907959","flag":"uploads/flags/flags/qa.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Romania","countryCode":"RO","dialCode":"+40","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090795a","flag":"uploads/flags/flags/ro.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Russia","countryCode":"RU","dialCode":"+7","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a1","flag":"uploads/flags/flags/ru.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Rwanda","countryCode":"RW","dialCode":"+250","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090795b","flag":"uploads/flags/flags/rw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Réunion","countryCode":"RE","dialCode":"+262","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a0","flag":"uploads/flags/flags/re.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Saint Barthélemy","countryCode":"BL","dialCode":"+590","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a2","flag":"uploads/flags/flags/bl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.609Z","updatedDateTime":"2020-04-01T16:04:53.609Z"},{"countryName":"Saint Helena, Ascension and Tristan Da Cunha","countryCode":"SH","dialCode":"+290","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a3","flag":"uploads/flags/flags/sh.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Saint Kitts and Nevis","countryCode":"KN","dialCode":"+1 869","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a4","flag":"uploads/flags/flags/kn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Saint Lucia","countryCode":"LC","dialCode":"+1 758","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a5","flag":"uploads/flags/flags/lc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Saint Martin","countryCode":"MF","dialCode":"+590","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a6","flag":"uploads/flags/flags/mf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Saint Pierre and Miquelon","countryCode":"PM","dialCode":"+508","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a7","flag":"uploads/flags/flags/pm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Saint Vincent and the Grenadines","countryCode":"VC","dialCode":"+1 784","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a8","flag":"uploads/flags/flags/vc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Samoa","countryCode":"WS","dialCode":"+685","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090795c","flag":"uploads/flags/flags/ws.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"San Marino","countryCode":"SM","dialCode":"+378","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090795d","flag":"uploads/flags/flags/sm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.610Z","updatedDateTime":"2020-04-01T16:04:53.610Z"},{"countryName":"Sao Tome and Principe","countryCode":"ST","dialCode":"+239","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079a9","flag":"uploads/flags/flags/st.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.611Z","updatedDateTime":"2020-04-01T16:04:53.611Z"},{"countryName":"Saudi Arabia","countryCode":"SA","dialCode":"+966","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090795e","flag":"uploads/flags/flags/sa.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.611Z","updatedDateTime":"2020-04-01T16:04:53.611Z"},{"countryName":"Senegal","countryCode":"SN","dialCode":"+221","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090795f","flag":"uploads/flags/flags/sn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Serbia","countryCode":"RS","dialCode":"+381","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907960","flag":"uploads/flags/flags/rs.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Seychelles","countryCode":"SC","dialCode":"+248","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907961","flag":"uploads/flags/flags/sc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Sierra Leone","countryCode":"SL","dialCode":"+232","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907962","flag":"uploads/flags/flags/sl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Singapore","countryCode":"SG","dialCode":"+65","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907963","flag":"uploads/flags/flags/sg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Slovakia","countryCode":"SK","dialCode":"+421","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907964","flag":"uploads/flags/flags/sk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Slovenia","countryCode":"SI","dialCode":"+386","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907965","flag":"uploads/flags/flags/si.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.618Z","updatedDateTime":"2020-04-01T16:04:53.618Z"},{"countryName":"Solomon Islands","countryCode":"SB","dialCode":"+677","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907966","flag":"uploads/flags/flags/sb.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.619Z","updatedDateTime":"2020-04-01T16:04:53.619Z"},{"countryName":"Somalia","countryCode":"SO","dialCode":"+252","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079aa","flag":"uploads/flags/flags/so.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.619Z","updatedDateTime":"2020-04-01T16:04:53.619Z"},{"countryName":"South Africa","countryCode":"ZA","dialCode":"+27","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907967","flag":"uploads/flags/flags/za.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.619Z","updatedDateTime":"2020-04-01T16:04:53.619Z"},{"countryName":"South Georgia and the South Sandwich Islands","countryCode":"GS","dialCode":"+500","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907968","flag":"uploads/flags/flags/gs.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.619Z","updatedDateTime":"2020-04-01T16:04:53.619Z"},{"countryName":"Spain","countryCode":"ES","dialCode":"+34","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907969","flag":"uploads/flags/flags/es.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.619Z","updatedDateTime":"2020-04-01T16:04:53.619Z"},{"countryName":"Sri Lanka","countryCode":"LK","dialCode":"+94","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090796a","flag":"uploads/flags/flags/lk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.619Z","updatedDateTime":"2020-04-01T16:04:53.619Z"},{"countryName":"Sudan","countryCode":"SD","dialCode":"+249","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090796b","flag":"uploads/flags/flags/sd.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"SuricountryName","countryCode":"SR","dialCode":"+597","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090796c","flag":"uploads/flags/flags/sr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Svalbard and Jan Mayen","countryCode":"SJ","dialCode":"+47","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079ab","flag":"uploads/flags/flags/sj.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Swaziland","countryCode":"SZ","dialCode":"+268","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090796d","flag":"uploads/flags/flags/sz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Sweden","countryCode":"SE","dialCode":"+46","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090796e","flag":"uploads/flags/flags/se.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Switzerland","countryCode":"CH","dialCode":"+41","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090796f","flag":"uploads/flags/flags/ch.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Syrian Arab Republic","countryCode":"SY","dialCode":"+963","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079ac","flag":"uploads/flags/flags/sy.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Taiwan, Province of China","countryCode":"TW","dialCode":"+886","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079ad","flag":"uploads/flags/flags/tw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.621Z","updatedDateTime":"2020-04-01T16:04:53.621Z"},{"countryName":"Tajikistan","countryCode":"TJ","dialCode":"+992","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907970","flag":"uploads/flags/flags/tj.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Tanzania, United Republic of","countryCode":"TZ","dialCode":"+255","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079ae","flag":"uploads/flags/flags/tz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Thailand","countryCode":"TH","dialCode":"+66","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907971","flag":"uploads/flags/flags/th.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Timor-Leste","countryCode":"TL","dialCode":"+670","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079af","flag":"uploads/flags/flags/tl.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Togo","countryCode":"TG","dialCode":"+228","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907972","flag":"uploads/flags/flags/tg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Tokelau","countryCode":"TK","dialCode":"+690","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907973","flag":"uploads/flags/flags/tk.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Tonga","countryCode":"TO","dialCode":"+676","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907974","flag":"uploads/flags/flags/to.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.622Z","updatedDateTime":"2020-04-01T16:04:53.622Z"},{"countryName":"Trinidad and Tobago","countryCode":"TT","dialCode":"+1 868","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907975","flag":"uploads/flags/flags/tt.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Tunisia","countryCode":"TN","dialCode":"+216","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907976","flag":"uploads/flags/flags/tn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Turkey","countryCode":"TR","dialCode":"+90","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907977","flag":"uploads/flags/flags/tr.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Turkmenistan","countryCode":"TM","dialCode":"+993","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907978","flag":"uploads/flags/flags/tm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Turks and Caicos Islands","countryCode":"TC","dialCode":"+1 649","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907979","flag":"uploads/flags/flags/tc.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Tuvalu","countryCode":"TV","dialCode":"+688","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090797a","flag":"uploads/flags/flags/tv.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Uganda","countryCode":"UG","dialCode":"+256","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090797b","flag":"uploads/flags/flags/ug.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.623Z","updatedDateTime":"2020-04-01T16:04:53.623Z"},{"countryName":"Ukraine","countryCode":"UA","dialCode":"+380","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090797c","flag":"uploads/flags/flags/ua.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"United Arab Emirates","countryCode":"AE","dialCode":"+971","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090797d","flag":"uploads/flags/flags/ae.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"United Kingdom","countryCode":"GB","dialCode":"+44","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090797e","flag":"uploads/flags/flags/gb.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"United States","countryCode":"US","dialCode":"+1","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e1090797f","flag":"uploads/flags/flags/us.png","maxlength":10,"minLength":10,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"Uruguay","countryCode":"UY","dialCode":"+598","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907980","flag":"uploads/flags/flags/uy.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"Uzbekistan","countryCode":"UZ","dialCode":"+998","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907981","flag":"uploads/flags/flags/uz.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"Vanuatu","countryCode":"VU","dialCode":"+678","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907982","flag":"uploads/flags/flags/vu.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"Venezuela, Bolivarian Republic of","countryCode":"VE","dialCode":"+58","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079b0","flag":"uploads/flags/flags/ve.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.624Z","updatedDateTime":"2020-04-01T16:04:53.624Z"},{"countryName":"Viet Nam","countryCode":"VN","dialCode":"+84","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079b1","flag":"uploads/flags/flags/vn.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"},{"countryName":"Virgin Islands, British","countryCode":"VG","dialCode":"+1 284","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079b2","flag":"uploads/flags/flags/vg.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"},{"countryName":"Virgin Islands, U.S.","countryCode":"VI","dialCode":"+1 340","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e109079b3","flag":"uploads/flags/flags/vi.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"},{"countryName":"Wallis and Futuna","countryCode":"WF","dialCode":"+681","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907983","flag":"uploads/flags/flags/wf.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"},{"countryName":"Yemen","countryCode":"YE","dialCode":"+967","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907984","flag":"uploads/flags/flags/ye.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"},{"countryName":"Zambia","countryCode":"ZM","dialCode":"+260","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907985","flag":"uploads/flags/flags/zm.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"},{"countryName":"Zimbabwe","countryCode":"ZW","dialCode":"+263","status":"","createdBy":"","updatedBy":"","_id":"5b4da340cd28642e10907986","flag":"uploads/flags/flags/zw.png","maxlength":10,"minLength":8,"createdDateTime":"2020-04-01T16:04:53.625Z","updatedDateTime":"2020-04-01T16:04:53.625Z"}]}

    resp = jsonify(country_dial_code_dict)
    resp.status_code = 200
    resp.mimetype = 'application/json'
    print(resp)
    return resp




# Home page route for site status
@app.route('/')
def homepage():
    data = request.get_data()
    header = dict(request.headers)
    if data:
        card_id = request.args.get('custom_data')
        print(card_id)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
        if 2==1:
            abort(404)
        else:
            print("Homepage")
    #send_email('sales.accessnumberstore@gmail.com', message)
    return ('Welcome to the Adphone Serverless API!', 200)


# Add credit to existing customer
@app.route('/v1/adphone/credit/update/', methods=['GET', 'POST'])
def update_credit():
    data = request.get_data()
    header = dict(request.headers)
    card_id = request.args.get('custom_data')
    print(card_id)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        reward_item = request.args.get('reward_item')
        card_data = request.args.get('custom_data')
        account_number = card_data['username']
        account_number = str(account_number)
        id_token = card_data['useralias']
        reward_amount = request.args.get('reward_amount')
        transaction_id = request.args.get('transaction_id')
        coin_value = 0.01
        credit_amount = reward_amount * coin_value
        print(str(credit_amount))
        print(str(transaction_id))
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where((Card.useralias == id_token) & (Card.username == account_number))
        print(query)
        card = query.execute()

        if not card:

            customer_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 0,
                                    description = "Add Credit issue - card not found. check in A2B - card # " + str(account_number),
                                    id_component = 7,
                                    priority = 3,
                                    status = 0,
                                    title = "Add Credit issue - " + str(account_number)
                                    )
            data = {

            }

            message = {
                    'success': 0,
                    'status': 406,
                    'message': 'Card not found',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp
        else:
            #credit = float(request.json['credit'])
            print(card[0].id)
            print(card[0].credit)
            print(card[0].phone)
            prev_credit = card[0].credit
            new_balance = prev_credit + float(credit_amount)
            firstname = card[0].firstname
            lastname = card[0].lastname
            phone = card[0].phone
            Card.update(credit=new_balance).where(Card.username == account_number).execute()


            # add logrefill
            logrefill = Logrefill(card=card[0].id, description=account_number, date=str(datetime.datetime.now()), credit=credit_amount, refill_type=0)
            logrefill.save()

            # add logpayment
            logpayment = Logpayment(card=card[0].id, date=str(datetime.datetime.now()), payment=credit_amount, payment_type=0, id_logrefill=logrefill.id)
            logpayment.save()

            # prepare dictionary for JSON return
            data = {
                'account_number': account_number,
                'current_balance': new_balance,
                'credited': credit_amount,
                'datetime': str(datetime.datetime.now()),
                'logrefill_id': logrefill.id,
                'logpayment_id': logpayment.id
            }
            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'Credit Updated',
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            print(resp.mimetype)
            return resp


# Add validity to existing customer
@app.route('/v1/adphone/expirationdate/update/', methods=['GET', 'POST'])
def update_expirationdate():
    data = request.get_data()
    header = dict(request.headers)
    card_id = request.args.get('custom_data')
    print(card_id)
    #verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-Sha256'))
    if 2==1:
        abort(404)
    else:
        req_data = json.loads(data.decode('utf-8'))
        print(req_data)
        print("Entering else..")
        reward_item = request.args.get('reward_item')
        card_data = request.args.get('custom_data')
        account_number = card_data['username']
        account_number = str(account_number)
        id_token = card_data['useralias']
        reward_amount = request.args.get('reward_amount')
        transaction_id = request.args.get('transaction_id')
        coin_value = 0.01
        credit_amount = reward_amount * coin_value
        print(str(credit_amount))
        print(str(transaction_id))
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.expirationdate, Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where((Card.useralias == id_token) & (Card.username == account_number))
        print(query)
        card = query.execute()

        if not card:

            customer_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 0,
                                    description = "Add Credit issue - card not found. check in A2B - card # " + str(account_number),
                                    id_component = 7,
                                    priority = 3,
                                    status = 0,
                                    title = "Add Credit issue - " + str(account_number)
                                    )
            data = {

            }

            message = {
                    'success': 0,
                    'status': 406,
                    'message': 'Card not found',
                    'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            return resp
        else:
            #credit = float(request.json['credit'])
            print(card[0].expirationdate)
            print(card[0].id)
            print(card[0].credit)
            print(card[0].phone)
            current_expiration_date = card[0].expirationdate

            if current_expiration_date < datetime.datetime.now():
                new_expiration_date = str(datetime.datetime.now() + datetime.timedelta(int(reward_amount)))
            else:
                new_expiration_date = str(datetime.datetime.now() + datetime.timedelta(int(reward_amount)))


            firstname = card[0].firstname
            lastname = card[0].lastname
            phone = card[0].phone
            Card.update(expirationdate=new_expiration_date, status=1).where(Card.username == account_number).execute()

            # prepare dictionary for JSON return
            data = {
                'account_number': account_number,
                'current_expiration_date': current_expiration_date,
                'new_expiration_date': new_expiration_date,
                'datetime': str(datetime.datetime.now()),
            }
            message = {
                        'success': 1,
                        'status': 200,
                        'message': 'Expiration Date Updated',
                        'customer': data
            }

            resp = jsonify(message)
            resp.status_code = 200
            resp.mimetype = 'application/json'
            print(resp)
            print(resp.mimetype)
            return resp







# function to send sms
def send_sms(phone_number, message):
        print(" **** ready to send SMS ****")
        # Initialize SNS client for Ireland region
        session = boto3.Session(
            region_name="eu-west-1"
        )
        sns_client = session.client('sns')
        # Send message
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'ANS'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        return (200)




# function to add ticket comment
def add_ticket_comment(message, ticket_id):
            TicketComment.create(
                                    creator = 2,
                                    creator_type = 1,
                                    date = str(datetime.datetime.now()),
                                    description = message,
                                    id_ticket = ticket_id
                                )


# function to send email
def send_email(recipient, email_subject, email_body_text, email_body_html):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Access Number Store <no-reply@accessnumberstore.com>"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipient

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "eu-west-1"

    # The subject line for the email.
    SUBJECT = email_subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (email_body_text
                )

    # The HTML body of the email.
    BODY_HTML = email_body_html

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    return (200)
