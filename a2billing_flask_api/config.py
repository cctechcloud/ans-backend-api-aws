# config


class Configuration(object):
    # Configure your A2Billing database peewee.MySQLDatabase
    DATABASE = {
        'host': '159.65.17.220',
        'port': 3306,
        'name': 'mya2billing',
        'engine': 'INNODB',
        'user': 'a2billinguser',
        'passwd': 'a2billing',
    }
    DEBUG = True
    # Set the secret key.  keep this really secret
    # Default implementation stores all session data in a signed cookie. This requires that the secret_key is set
    SECRET_KEY = 'cctechsecret'
