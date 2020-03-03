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
import os
from app import mail
from flask_mail import Mail, Message
import boto3
from botocore.exceptions import ClientError




country_code_dict = {"BD": "Bangladesh", "BE": "Belgium", "BF": "Burkina Faso", "BG": "Bulgaria", "BA": "Bosnia and Herzegovina", "BB": "Barbados", "WF": "Wallis and Futuna", "BL": "Saint Barthelemy", "BM": "Bermuda", "BN": "Brunei", "BO": "Bolivia", "BH": "Bahrain", "BI": "Burundi", "BJ": "Benin", "BT": "Bhutan", "JM": "Jamaica", "BV": "Bouvet Island", "BW": "Botswana", "WS": "Samoa", "BQ": "Bonaire, Saint Eustatius and Saba ", "BR": "Brazil", "BS": "Bahamas", "JE": "Jersey", "BY": "Belarus", "BZ": "Belize", "RU": "Russia", "RW": "Rwanda", "RS": "Serbia", "TL": "East Timor", "RE": "Reunion", "TM": "Turkmenistan", "TJ": "Tajikistan", "RO": "Romania", "TK": "Tokelau", "GW": "Guinea-Bissau", "GU": "Guam", "GT": "Guatemala", "GS": "South Georgia and the South Sandwich Islands", "GR": "Greece", "GQ": "Equatorial Guinea", "GP": "Guadeloupe", "JP": "Japan", "GY": "Guyana", "GG": "Guernsey", "GF": "French Guiana", "GE": "Georgia", "GD": "Grenada", "GB": "United Kingdom", "GA": "Gabon", "SV": "El Salvador", "GN": "Guinea", "GM": "Gambia", "GL": "Greenland", "GI": "Gibraltar", "GH": "Ghana", "OM": "Oman", "TN": "Tunisia", "JO": "Jordan", "HR": "Croatia", "HT": "Haiti", "HU": "Hungary", "HK": "Hong Kong", "HN": "Honduras", "HM": "Heard Island and McDonald Islands", "VE": "Venezuela", "PR": "Puerto Rico", "PS": "Palestinian Territory", "PW": "Palau", "PT": "Portugal", "SJ": "Svalbard and Jan Mayen", "PY": "Paraguay", "IQ": "Iraq", "PA": "Panama", "PF": "French Polynesia", "PG": "Papua New Guinea", "PE": "Peru", "PK": "Pakistan", "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland", "PM": "Saint Pierre and Miquelon", "ZM": "Zambia", "EH": "Western Sahara", "EE": "Estonia", "EG": "Egypt", "ZA": "South Africa", "EC": "Ecuador", "IT": "Italy", "VN": "Vietnam", "SB": "Solomon Islands", "ET": "Ethiopia", "SO": "Somalia", "ZW": "Zimbabwe", "SA": "Saudi Arabia", "ES": "Spain", "ER": "Eritrea", "ME": "Montenegro", "MD": "Moldova", "MG": "Madagascar", "MF": "Saint Martin", "MA": "Morocco", "MC": "Monaco", "UZ": "Uzbekistan", "MM": "Myanmar", "ML": "Mali", "MO": "Macao", "MN": "Mongolia", "MH": "Marshall Islands", "MK": "Macedonia", "MU": "Mauritius", "MT": "Malta", "MW": "Malawi", "MV": "Maldives", "MQ": "Martinique", "MP": "Northern Mariana Islands", "MS": "Montserrat", "MR": "Mauritania", "IM": "Isle of Man", "UG": "Uganda", "TZ": "Tanzania", "MY": "Malaysia", "MX": "Mexico", "IL": "Israel", "FR": "France", "IO": "British Indian Ocean Territory", "SH": "Saint Helena", "FI": "Finland", "FJ": "Fiji", "FK": "Falkland Islands", "FM": "Micronesia", "FO": "Faroe Islands", "NI": "Nicaragua", "NL": "Netherlands", "NO": "Norway", "NA": "Namibia", "VU": "Vanuatu", "NC": "New Caledonia", "NE": "Niger", "NF": "Norfolk Island", "NG": "Nigeria", "NZ": "New Zealand", "NP": "Nepal", "NR": "Nauru", "NU": "Niue", "CK": "Cook Islands", "XK": "Kosovo", "CI": "Ivory Coast", "CH": "Switzerland", "CO": "Colombia", "CN": "China", "CM": "Cameroon", "CL": "Chile", "CC": "Cocos Islands", "CA": "Canada", "CG": "Republic of the Congo", "CF": "Central African Republic", "CD": "Democratic Republic of the Congo", "CZ": "Czech Republic", "CY": "Cyprus", "CX": "Christmas Island", "CR": "Costa Rica", "CW": "Curacao", "CV": "Cape Verde", "CU": "Cuba", "SZ": "Swaziland", "SY": "Syria", "SX": "Sint Maarten", "KG": "Kyrgyzstan", "KE": "Kenya", "SS": "South Sudan", "SR": "Suriname", "KI": "Kiribati", "KH": "Cambodia", "KN": "Saint Kitts and Nevis", "KM": "Comoros", "ST": "Sao Tome and Principe", "SK": "Slovakia", "KR": "South Korea", "SI": "Slovenia", "KP": "North Korea", "KW": "Kuwait", "SN": "Senegal", "SM": "San Marino", "SL": "Sierra Leone", "SC": "Seychelles", "KZ": "Kazakhstan", "KY": "Cayman Islands", "SG": "Singapore", "SE": "Sweden", "SD": "Sudan", "DO": "Dominican Republic", "DM": "Dominica", "DJ": "Djibouti", "DK": "Denmark", "VG": "British Virgin Islands", "DE": "Germany", "YE": "Yemen", "DZ": "Algeria", "US": "United States", "UY": "Uruguay", "YT": "Mayotte", "UM": "United States Minor Outlying Islands", "LB": "Lebanon", "LC": "Saint Lucia", "LA": "Laos", "TV": "Tuvalu", "TW": "Taiwan", "TT": "Trinidad and Tobago", "TR": "Turkey", "LK": "Sri Lanka", "LI": "Liechtenstein", "LV": "Latvia", "TO": "Tonga", "LT": "Lithuania", "LU": "Luxembourg", "LR": "Liberia", "LS": "Lesotho", "TH": "Thailand", "TF": "French Southern Territories", "TG": "Togo", "TD": "Chad", "TC": "Turks and Caicos Islands", "LY": "Libya", "VA": "Vatican", "VC": "Saint Vincent and the Grenadines", "AE": "United Arab Emirates", "AD": "Andorra", "AG": "Antigua and Barbuda", "AF": "Afghanistan", "AI": "Anguilla", "VI": "U.S. Virgin Islands", "IS": "Iceland", "IR": "Iran", "AM": "Armenia", "AL": "Albania", "AO": "Angola", "AQ": "Antarctica", "AS": "American Samoa", "AR": "Argentina", "AU": "Australia", "AT": "Austria", "AW": "Aruba", "IN": "India", "AX": "Aland Islands", "AZ": "Azerbaijan", "IE": "Ireland", "ID": "Indonesia", "UA": "Ukraine", "QA": "Qatar", "MZ": "Mozambique"}
inv_country_code_dict = {v: k for k, v in country_code_dict.items()}

support_email = os.environ.get("SUPPORT_EMAIL")
support_phone_number = os.environ.get("SUPPORT_PHONE_NUMBER")
portal_url = os.environ.get("PORTAL_URL")

shopify_secret_key = os.environ.get("SHOPIFY_SECRET_KEY")
shopify_secret_key = shopify_secret_key.encode()

# function to verify web hook data
def verify_webhook(data, hmac_header):
    print(" **** data from verify_webhook ****")
    digest = hmac.new(shopify_secret_key, data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

# ***** function to check avaiibile phone numbers in the country ******
def onboarding(country, email, amount, order_number, ticket_id, destination, expiry_date, req_data):

    country_code = inv_country_code_dict[country]

    # step 1 :  check and buy a phone number for a country under Twilio account
    # Don't hardcode. Load it from Environment variable.
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
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

    # Purchase the phone number from Twilio
    incoming_phone_number = client.incoming_phone_numbers \
                .create(phone_number=available_phone_number, address_sid=os.environ.get("TWILIO_ADDRESS_SID")) \
                .update(voice_application_sid=os.environ.get("TWILIO_TWIMLAPP_SID"))
    # *****  create A2B card for that phone number, create DiD, create DidDestination  ******
    pin = random.randint(1000,9999)
    passcode = 'ANS' + email + str(pin) + str(order_number)

    firstname = req_data['customer']['default_address']['first_name']
    lastname = req_data['customer']['default_address']['last_name']
    address = req_data['customer']['default_address']['address1']
    city = req_data['customer']['default_address']['city']
    state = req_data['customer']['default_address']['address2']
    customer_country = req_data['customer']['default_address']['country']
    customer_country_code = inv_country_code_dict[customer_country]
    zipcode = req_data['customer']['default_address']['zip']
    #phone = req_data['customer']['default_address']['phone']
    phone = destination
    company_name = req_data['customer']['default_address']['company']

    # step 2 : Create Card
    card = Card.create(username= account_number, useralias= account_number, uipass= passcode, email= email, sip_buddy= 1, lock_pin= pin, country= customer_country_code, expirationdate= expiry_date, enableexpire= '1', firstname= firstname, lastname= lastname, address= address, city= city, state= state, zipcode= zipcode, phone= phone, company_name= company_name, tariff= country, voicemail_permitted= 1, voicemail_activated= 1, email_notification= email, notify_email= 1, credit_notification= 1)
    print(card.username)       #
    add_ticket_comment("Card created with id: " + str(card.id) + " and username: " + account_number + " and country: " + country, order_number, ticket_id)
    sipbuddy = SipBuddies.create(username= account_number, accountcode= account_number, name = account_number, secret= passcode, id_cc_card= card.id, context= 'a2billing', regexten= '', callerid= '', fromuser= '', fromdomain= '', host= '', insecure= '', mailbox= '', md5secret= '', deny= '', mask= '', allow= '', musiconhold= '', fullcontact= '', setvar= '')
    '''
    message = client.messages.create(
             body="Dear Customer, Greetings from Access Number Store. Order # {}. Your Access Number is +{} For receiving calls, please download the below-recommended softphone app and Create Account using your mobile number {}. LINPHONE FOR IPHONE https://itunes.apple.com/us/app/linphone/id360065638?mt=8  LINPHONE FOR ANDROID https://play.google.com/store/apps/details?id=org.linphone&hl=en_GB".format(order_number, account_number, phone),
             from_=os.environ.get("SMS_PHONE_NUMBER"),
             to=destination
    )
    '''
    message= "Dear Customer, Greetings from Access Number Store. Order # {}. Your Access Number is +{} For receiving calls, please download the below-recommended softphone app and Create Account using your mobile number {}. Go to 'Settings'-> Your account -> ensure Push Notification is ON and Account enabled is ON. LINPHONE FOR IPHONE https://itunes.apple.com/us/app/linphone/id360065638?mt=8  LINPHONE FOR ANDROID https://play.google.com/store/apps/details?id=org.linphone&hl=en_GB".format(order_number, account_number, phone)
    send_sms(phone, message)
    add_ticket_comment("SMS sent to Customer on his destination mobile number : " + phone + " for order number ", order_number, ticket_id)

    if not card.email:
        msg = Message('Order {} fullfillment in progress...'.format(order_number), recipients=[email, support_email])

        customer_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 0,
                                    description = "Oboarding issue - card not found. check in A2B - card # " + card.username,
                                    id_component = 7,
                                    priority = 3,
                                    status = 0,
                                    title = "Oboarding issue - " + str(order_number)
                                    )
        '''
        msg.body = 'Our fulfillment team is currently processing your request. We will email you soon once the order is fulfilled.'
        msg.html = '<p>Hello {} {} </p> <h1>Your Order # {} is being processed.</h1> <p>Our fulfillment team is currently processing your request.</p>  <p>You will recieve an email soon once the order is fulfilled.</p>  <p>   </p>  <p> If you have any questions, please contact us on email us at {}</p> <p>Thank you,<br>Access Number Store</p>'.format(firstname, lastname, order_number, support_phone_number, support_email)
        mail.send(msg)
        '''
        email_subject = 'Your Order # {} is being processed'.format(order_number)
        email_body_text = 'Dear Customer, Greetings from Access Number Store. Your Order # {} is being processed. You will recieve an email soon once the order is fulfilled.  If you have any questions meanwhile, please contact us through Portal or email us at {}'.format(order_number, support_phone_number, support_email)
        email_body_html = """<html>
        <head></head>
        <body>
          <p>'Dear Customer, Greetings from Access Number Store. Your Order # {} is being processed. You will recieve an email soon once the order is fulfilled.  If you have any questions meanwhile, please contact us through Portal or email us at {} </p>'
        </body>
        </html>
        """.format(order_number, support_phone_number, support_email)
        send_email(email, email_subject, email_body_text, email_body_html)
        add_ticket_comment("Order fullfillment in progress email for username: " + account_number + " sent to customer's email : " + email, order_number, ticket_id)

        add_ticket_comment("Our fulfillment team is currently processing your request. We will email you soon once the order is fulfilled to your email at" + email, order_number, str(customer_ticket.id))
        add_ticket_comment("New support ticket created for this issue with ID # " + str(customer_ticket.id) + " sent to customer's email : " + email, order_number, ticket_id)
    else:
        access_number = "+" + card.username
        #msg = Message('Order {} fulfilled successfully'.format(order_number), recipients=[card.email])
        #msg.body = 'Order {} fulfilled.'.format(order_number)
        email_subject = 'Order {} fulfilled successfully'.format(order_number)
        email_body_text = '''Hello {} {}, Greetings from Access Number Store. Order # {} fulfilled successfully. Your Access Number : {}. Please download the below recommended softphone app on to your phone. Once downloaded, CREATE ACCOUNT in the app.
        DOWNLOAD LINPHONE FOR IPHONE
        https://itunes.apple.com/us/app/linphone/id360065638?mt=8
        DOWNLOAD LINPHONE FOR ANDROID
        https://play.google.com/store/apps/details?id=org.linphone&hl=en_GB </p>
        Your access number account details are provided below username : {} password : {}   You can sign in to customer portal using above credentials after clicking on Portal in the following url : {} Once logged in, you will be able to check account details / balance / call rates / call history and create support tickets. <p> If you have any questions, please contact us through Portal or email us at {} Thank you, Access Number Store '''.format(firstname, lastname, order_number, access_number, destination, card.useralias, card.uipass, portal_url, support_phone_number, support_email)
        email_body_html = '''<html>
                             <head>Order # {} is fulfilled successfully.</head>
                             <body>
                               <p>Hello {} {} </p> <h3>Your Access Number : {} </h3>
                               <h4>Incoming calls to your access number will be delivered to softphone app on your phone {} as requested.</h4>
                               <p>Please download the below recommended softphone app on to your phone.</p>
                               <p>Once downloaded, CREATE ACCOUNT in the softphone app using your phone number.</p>
                               <p>Go to 'Settings' --> Click on your account(phone number) -->  Ensure 'Push Notification' is turned ON --> Ensure 'Account enabled' is turned ON </p>
                                 <p>DOWNLOAD LINPHONE FOR IPHONE</p>
                                 <p>https://itunes.apple.com/us/app/linphone/id360065638?mt=8 </p>
                                 <p>DOWNLOAD LINPHONE FOR ANDROID</p>
                                 <p>https://play.google.com/store/apps/details?id=org.linphone&hl=en_GB </p>
                                 <p>Your access number account details are provided below</p>
                                 <p>username : {}</p>
                                 <p>password : {}</p>
                                 <p>You can sign in to customer portal using above credentials after clicking on Portal in the following url : {}</p>
                                 <p>Once logged in, you will be able to check account details / balance / call history and create support tickets.</p>
                                 <p> If you have any questions, please contact us through Portal or email us at {}</p>
                                 <p>Thank you,<br>Access Number Store</p>
                            </body>
                            </html>'''.format(order_number, firstname, lastname, access_number, destination, card.useralias, card.uipass, portal_url, support_phone_number, support_email)
        send_email(email, email_subject, email_body_text, email_body_html)

        add_ticket_comment("Order fullfillment completed email for username: " + account_number + " sent to customer's email : " + str(card.email), order_number, ticket_id)


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
                            selling_rate= 0.02,
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
                            aleg_retail_cost_min = 0.02,
                            aleg_retail_cost_min_offp = 0.02,
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
    #did_destination_2 = DidDestination.create(destination= stripped_destination, priority= 2, id_cc_card= card.id, id_cc_did= did.id, activated= 1, voip_call= 0, validated= 0)

    add_ticket_comment("DiD Destinations created - did_destination_1: " + str(did_destination_1.destination), order_number, ticket_id)
    # step 4 :  add credit in a2billing
    topup_amount =  amount
    buy_topup(account_number, email, topup_amount, order_number, ticket_id)
    # step 5 :  email and sms customer on completion of the order
    # step 6 :  craete voicemail for this card
    vm = VoicemailUsers.create(email= email, mailbox= account_number, delete = 'yes', context= 'default')
    add_ticket_comment("Voicemailbox created for user " + str(account_number), order_number, ticket_id)

    # step 7 :  create SIP Crendetial in Twilio
    credential_list = os.environ.get("TWILIO_SIPCREDENTIALLIST_SID")
    credential = client.sip.credential_lists(credential_list) \
                       .credentials \
                       .create(username=account_number, password=passcode)
    print("Onboarding Completed Successfully")
    return

# function to buy support Plan
def buy_supportplan(email, amount, order_number, ticket_id, expiry_date, req_data):
    country_code = 'BE'

    # step 1 :  check and buy a phone number for a country under Twilio account
    # Don't hardcode. Load it from Environment variable.
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
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
    print("New Support Access Code " + account_number + " has been selected")

    # *****  create A2B card for that phone number, create DiD, create DidDestination  ******
    pin = random.randint(1000,9999)
    passcode = 'ANS' + email + str(pin) + str(order_number)

    firstname = req_data['customer']['default_address']['first_name']
    lastname = req_data['customer']['default_address']['last_name']
    address = req_data['customer']['default_address']['address1']
    city = req_data['customer']['default_address']['city']
    state = req_data['customer']['default_address']['address2']
    customer_country = req_data['customer']['default_address']['country']
    customer_country_code = inv_country_code_dict[customer_country]
    zipcode = req_data['customer']['default_address']['zip']
    phone = req_data['customer']['default_address']['phone']
    #phone = destination
    company_name = 'support'
    credit = '9.99'
    new_credit = float(credit)

    # step 2 : Create Card
    card = Card.create(username= account_number, useralias= account_number, uipass= passcode, email= email, sip_buddy= 0, lock_pin= pin, country= customer_country_code, expirationdate= expiry_date, enableexpire= '1', firstname= firstname, lastname= lastname, address= address, city= city, state= state, zipcode= zipcode, phone= phone, company_name= company_name, tariff= 'support', voicemail_permitted= 0, voicemail_activated= 0, email_notification= email, notify_email= 0, credit_notification= 0, credit= new_credit)
    print(card.username)       #
    add_ticket_comment("Support Access Code - Card created with id: " + str(card.id) + " and username: " + account_number, order_number, ticket_id)

    # step 3 : email customer
    email_subject = 'Order {} fulfilled successfully'.format(order_number)
    email_body_text = 'Dear Customer, Greetings from Access Number Store. Order # {} fulfilled successfully. Your Support Access Code : {}'.format(order_number, account_number)
    email_body_html = """<html>
    <head>Order # {} fulfilled successfully.</head>
    <body>
    <p>Dear Customer,</p>
    <p>Greetings from Access Number Store. </p>
    <p>Your Support Access Code: {}</p>
    <p>You will need to provide this Support Access Code when calling our Support Phone Numbers. </p>
    <p>Our Support Phone Numbers are listed in the Portal.</p>
    <p>Thank you for using our service.</p>
    </body>
    </html>
    """.format(order_number, account_number)
    print("email address is: " + email )
    send_email(email, email_subject, email_body_text, email_body_html)
    return


# function to add buy topup
def buy_topup(account_number, email, topup_amount, order_number, ticket_id):
    # ***** test this code for buying topup *****
        account_number = str(account_number)
        credit = topup_amount
        access_number = "+" + account_number
        # Get Card(vat, credit) - using useraliad only for testing
        query = Card.select(Card.credit, Card.id, Card.firstname, Card.lastname, Card.phone).where(Card.username == account_number)
        card = query.execute()

        if not card:

            customer_ticket = Ticket.create(
                                    creationdate = str(datetime.datetime.now()),
                                    creator = 2,
                                    creator_type = 0,
                                    description = "Topup issue - card not found. check in A2B - card # " + account_number,
                                    id_component = 7,
                                    priority = 3,
                                    status = 0,
                                    title = "Topup issue - " + str(order_number)
                                    )
            '''
            msg = Message('Order {} fullfillment - Discrepancy observed - Need more information - Ticket # {}'.format(order_number, str(customer_ticket.id)), recipients=[email, support_email])
            msg.body = 'Our fulfillment team has observed a discrepancy while processing your request.'
            msg.html = '<p>Hello</p>  <h1>Your Order # {} is being processed.</h1> <p>Our fulfillment team has observed a discrepancy while processing your request.</p>  <h4>Phone number you have requested to top up does not exist in our system.</h4>  <p>Please check the same in your order and please contact our support team through Portal or email at {} to update your order.</p> <p>Thank you,<br>Access Number<br>Online Store</p>'.format(order_number, support_phone_number, support_email)
            mail.send(msg)
            '''
            email_subject = 'Order # {} fullfillment - Discrepancy observed - Need more information - Ticket # {}'.format(order_number, str(customer_ticket.id))
            email_body_text = 'Dear Customer, Greetings from Access Number Store. Order # {}. Our fulfillment team has observed a discrepancy while processing your request. Access Number +{} you have requested to top up does not exist in our system. Please check your Access Number from your order and contact our support team through Portal or email at {} to update your order. Thank You.'.format(order_number, account_number, support_phone_number, support_email)
            email_body_html = """<html>
            <head>Order # {}</head>
            <body>
              <p>Dear Customer,</p>
              <p>Greetings from Access Number Store. </p>
              <p>Our fulfillment team has observed a discrepancy while processing your request.</p>
              <p> Access Number +{} you have requested to top up does not exist in our system. </p>
              <p>Please check your Access Number from your order and contact our support team through Portal or email at {} to update your order.</p>
              <p> Thank You.</p>
            </body>
            </html>
            """.format(order_number, account_number, support_phone_number, support_email)
            send_email(email, email_subject, email_body_text, email_body_html)

            add_ticket_comment("Order fullfillment - Discrepancy observed - Need more information from username: " + account_number + " sent to customer's email : " + email, order_number, str(customer_ticket.id))
            add_ticket_comment("New support ticket created for this issue with ID # " + str(customer_ticket.id) + " sent to customer's email : " + email, order_number, ticket_id)
            #return Response('Card not found.', 400)
        else:
            #credit = float(request.json['credit'])
            print(card[0].id)
            print(card[0].credit)
            print(card[0].phone)
            prev_credit = card[0].credit
            new_balance = prev_credit + float(credit)
            firstname = card[0].firstname
            lastname = card[0].lastname
            phone = card[0].phone
            revised_expiry_date = str(datetime.datetime.now() + datetime.timedelta(27))
            Card.update(credit=new_balance,expirationdate=revised_expiry_date).where(Card.username == account_number).execute()

            account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
            auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
            #trunk_sid = os.environ.get("TWILIO_TRUNK_SID")
            twimlapp_sid = os.environ.get("TWILIO_TWIMLAPP_SID")
            default_address_sid = "Address SID for default address"
            client = Client(account_sid, auth_token)
            incoming_phone_number_list = client.incoming_phone_numbers.list(phone_number=account_number,limit=2)
            # dis-associate sip trunk with access number
            for record in incoming_phone_number_list:
                incoming_phone_number = client.incoming_phone_numbers(record.sid).update(voice_application_sid=twimlapp_sid)

            add_ticket_comment("Top-up Successfull on card with username  " + account_number + " Previous Balance:  " + str(prev_credit) + " New Balance:  " + str(new_balance) , order_number, ticket_id)
            if prev_credit != 0.0:

                #msg = Message('Order {} fulfilled successfully'.format(order_number), recipients=[email])
                #msg.body = 'Order {} fulfilled.'.format(order_number)

                #msg.html = '''<p>Hello {} {} </p> <h4>Order # {} is fulfilled successfully.</h4> <h4>Your Access Number : {} is topped up with {} GBP</h4> <p>Previous Balance:  {} GBP </p> <p>   </p>  <p>Current Balance:  {} GBP  </p> <p> If you have any questions, please contact us through Portal or email us at {}</p> <p>Thank you,<br>Access Number<br>Online Store</p>'''.format(firstname, lastname, order_number, access_number, credit, prev_credit, new_balance, support_phone_number, support_email)
                #mail.send(msg)
                email_subject = 'Order {} fulfilled successfully'.format(order_number)
                email_body_text = 'Dear Customer, Greetings from Access Number Store. Order # {} fulfilled successfully. Your Access Number: +{} is topped up with {} GBP.'.format(order_number, account_number, credit)
                email_body_html = """<html>
                <head>Order # {} fulfilled successfully.</head>
                <body>
                  <p>Dear Customer,</p>
                  <p>Greetings from Access Number Store. </p>
                  <p>Your Access Number: +{} is topped up with {} GBP.</p>
                  <p>Thank you for using our service.</p>
                </body>
                </html>
                """.format(order_number, account_number, credit)
                print("email address is: " + email )
                send_email(email, email_subject, email_body_text, email_body_html)


                '''
                message = client.messages.create(
                         body="""Dear Customer, Greetings from Access Number Store. Order # {} is fulfilled successfully. Your Access Number : +{} is topped up with {} GBP. Previous Balance:  {} GBP Current Balance:  {} GBP. We hope you continue to enjoy our service.Thank you.""".format(order_number, account_number, credit, prev_credit, new_balance),
                         from_=os.environ.get("SMS_PHONE_NUMBER"),
                         to=phone
                )
                '''
                message= "Dear Customer, Greetings from Access Number Store. Order # {}. Your Access Number: +{} is topped up with {} GBP.".format(order_number, account_number, credit)
                send_sms(phone, message)
                add_ticket_comment("SMS sent to Customer on his destination mobile number : " + phone + " for order number ", order_number, ticket_id)
                add_ticket_comment("Order fullfillment completed email for username: " + account_number + " sent to customer's email : " + email, order_number, ticket_id)


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



# function to add ticket comment
def add_ticket_comment(message, order_number, ticket_id):
            TicketComment.create(
                                    creator = 2,
                                    creator_type = 1,
                                    date = str(datetime.datetime.now()),
                                    description = message + " for order number: " +str(order_number),
                                    id_ticket = ticket_id
                                )

# Home page route for site status
@app.route('/')
def homepage():
    #send_sms('+447412678577', 'This is a test SMS from AWS')
    message = """<html>
    <head></head>
    <body>
      <h1>Amazon SES Test (SDK for Python)</h1>
      <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
          AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
                """
    #send_email('sales.accessnumberstore@gmail.com', message)
    return 'Welcome to Access Number Store Customer Onboarding API!'




# Paid Order Processing route
@app.route('/v1/order/paid/', methods=['POST'])

def paid_order():
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
            print("Webhook Retransmission - Skipping further Processing of Order number " + str(order_number) )
            return Response(status = 200)
        line_items_list = req_data['line_items']
        email = req_data['email']


        for product_name in line_items_list:
            if 'Top-up' in product_name['title']:
                apply_to_number = product_name['properties'][0]['value']
                print("Apply Topup to phone number" + apply_to_number)
                if not apply_to_number:
                        print("Topup phone number missing")
                        account_number = '5834639514'
                        add_ticket_comment("Topup phone number missing in the data payload properties", order_number, new_ticket.id)
                else:
                        account_number = apply_to_number.lstrip('+')
                        print(account_number)

                amount = product_name['price']
                print(account_number, product_name['price'], amount)
                buy_topup(account_number, email, amount, order_number, new_ticket.id)
            elif 'Support' in product_name['title']:
                print("Support Plan Purchased")
                country = product_name['title']
                email = req_data['email']
                amount = product_name['price']
                expiry_in_days = 28
                expiry_date = str(datetime.datetime.now() + datetime.timedelta(28))
                result = buy_supportplan(email, amount, order_number, new_ticket.id, expiry_date, req_data)
                print(result)

            else:
                country = product_name['title']
                email = req_data['email']
                amount = product_name['price']
                expiry_in_months = 1
                #expiry_in_days = (int(expiry_in_months) * 30) - 1
                expiry_in_days = 28
                expiry_date = str(datetime.datetime.now() + datetime.timedelta(28))
                forward_to_number = product_name['properties'][0]['value']
                print("Forward to phone number is" + forward_to_number)
                if not forward_to_number:
                        print("Forward to phone number i.e, Destination is missing")
                        destination = '+441793250311'
                        add_ticket_comment("Forward to phone number i.e, Destination is missing in the data payload properties..setting default destination", order_number, new_ticket.id)
                else:
                        destination = forward_to_number

                result = onboarding(country, email, amount, order_number, new_ticket.id, destination, expiry_date, req_data)
                print(result)

            Ticket.update(status=1,priority=1).where(Ticket.title == str(order_number)).execute()

        return Response(status = 200)


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
