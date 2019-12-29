# config


class Configuration(object):
    # Configure your A2Billing database peewee.MySQLDatabase
    DATABASE = {
        'host': 'red.ca0vcrcbf5na.eu-west-2.rds.amazonaws.com',
        'port': 3306,
        'name': 'mya2billing',
        'engine': 'peewee.MySQLDatabase',
        'user': 'a2billinguser',
        'passwd': 'Kr1shang',
    }

    DEBUG = True
    # Set the secret key.  keep this really secret
    # Default implementation stores all session data in a signed cookie. This requires that the secret_key is set
    SECRET_KEY = 'cctechsecret'
