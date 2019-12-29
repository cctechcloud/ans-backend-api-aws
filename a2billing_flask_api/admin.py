from flask_peewee.admin import Admin, ModelAdmin
from app import app
from auth import auth
from models import CardGroup, Card, Callerid, Logrefill, Logpayment, Call, Country, Charge, Did, DidDestination, CountryServer, Alarm, Ticket
# from models import Did, DidDestination


class CardAdmin(ModelAdmin):
    columns = ('id', 'username', 'creationdate', 'credit', 'status')


class CardGroupAdmin(ModelAdmin):
    columns = ('id', 'name',)


class CalleridAdmin(ModelAdmin):
    columns = ('id', 'id_cc_card', 'activated', 'cid',)


class LogrefillAdmin(ModelAdmin):
    columns = ('id', 'card', 'date', 'credit', 'refill_type',)


class LogpaymentAdmin(ModelAdmin):
    columns = ('id', 'card', 'date', 'payment', 'payment_type',)


class CallAdmin(ModelAdmin):
    columns = ('uniqueid','card_id', 'sessionid', 'starttime', 'stoptime', 'src', 'dnid', 'calledstation', 'real_sessiontime', 'buycost', 'sessionbill', 'terminatecauseid')


class CountryAdmin(ModelAdmin):
    columns = ('id', 'countrycode', 'countryname')


class ChargeAdmin(ModelAdmin):
    columns = ('id', 'id_cc_card', 'creationdate', 'amount', 'chargetype')


class DidAdmin(ModelAdmin):
    columns = ('id', 'did', 'iduser', 'activated', 'reserved')


class DidDestinationAdmin(ModelAdmin):
    columns = ('destination', 'id_cc_card', 'id_cc_did', 'activated')


class CountryServerAdmin(ModelAdmin):
    columns = ('id', 'countrycode', 'countryname', 'countryprefix', 'server', 'port')


class TicketAdmin(ModelAdmin):
    columns = ('id', 'title', 'description', 'creationdate', 'priority', 'creator', 'creator_type', 'id_component', 'status', 'viewed_cust', 'viewed_agent', 'viewed_admin' )


'''

admin = Admin(app, auth, branding='Redirect API Admin Site')
admin.register(Card, CardAdmin)
admin.register(CardGroup, CardGroupAdmin)
admin.register(Callerid, CalleridAdmin)
admin.register(Logrefill, LogrefillAdmin)
admin.register(Logpayment, LogpaymentAdmin)
admin.register(Call, CallAdmin)
admin.register(Country, CountryAdmin)
admin.register(Charge, ChargeAdmin)
admin.register(Did, DidAdmin)
admin.register(DidDestination, DidDestinationAdmin)
admin.register(CountryServer, CountryServerAdmin)
admin.register(Ticket, TicketAdmin)
auth.register_admin(admin)

'''
