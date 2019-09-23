from flask_peewee.rest import RestAPI, UserAuthentication, RestResource, RestrictOwnerResource
from flask import request
from auth import auth
from app import app
from models import CardGroup, Card, Callerid, Logrefill, Logpayment, Call, Country, Charge, Did, DidDestination, SipBuddies, Customer, Message
# from models import Did, DidDestination
import json


# create a special resource for users that excludes email and password
class CardResource(RestResource):
    # exclude = ('lock_pin',)

    def check_post(self):
        datajson = json.loads(request.data)
        if 'username' not in datajson or len(datajson['username']) == 0:
            return False
        if 'useralias' not in datajson or len(datajson['useralias']) == 0:
            return False
        if 'uipass' not in datajson or len(datajson['uipass']) == 0:
            return False
        if 'credit' not in datajson or len(datajson['credit']) == 0:
            return False
        if 'tariff' not in datajson or len(datajson['tariff']) == 0:
            return False

        return True


# create a special resource for users that excludes email and password
class UserResource(RestResource):
    exclude = ('password', 'email')


class CustomerResource(RestResource):
    exclude = ('password', 'email')



class MessageResource(RestrictOwnerResource):
    owner_field = 'user_id'

    '''
      # restrict PUT/DELETE to owner of an object, likewise apply owner to any
    # incoming POSTs
    owner_field = 'user'

    def validate_owner(self, user, obj):
        return user == getattr(obj, self.owner_field)

    def set_owner(self, obj, user):
        setattr(obj, self.owner_field, user)

    def check_put(self, obj):
        return self.validate_owner(g.user, obj)

    def check_delete(self, obj):
        return self.validate_owner(g.user, obj)

    def save_object(self, instance, raw_data):
        self.set_owner(instance, g.user)
        return super(RestrictOwnerResource, self).save_object(instance, raw_data)

    '''


# class LogrefillResource(RestResource):

#     def prepare_data(self, obj, data):
#         data["credit"] = str(data["credit"])
#         return data


# instantiate the user auth
user_auth = UserAuthentication(auth, protected_methods=['GET', 'POST', 'PUT', 'DELETE'])


# create a RestAPI container
api = RestAPI(app, default_auth=user_auth)
# register the models
api.register(Card, CardResource, auth=user_auth)
api.register(CardGroup, auth=user_auth)
api.register(Callerid, auth=user_auth)
api.register(Logrefill, auth=user_auth)
api.register(Logpayment, auth=user_auth)
api.register(Call, auth=user_auth)
api.register(Country, auth=user_auth)
api.register(Charge, auth=user_auth)
api.register(Did, auth=user_auth)
api.register(DidDestination, auth=user_auth)
api.register(SipBuddies, auth=user_auth)
api.register(Message, MessageResource, auth=user_auth)
