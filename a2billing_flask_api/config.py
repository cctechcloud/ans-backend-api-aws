# config


class Configuration(object):
    # Configure your A2Billing database peewee.MySQLDatabase
    DATABASE = {
        'host': os.environ.get("A2B_DB_HOST"),
        'port': 3306,
        'name': os.environ.get("A2B_DB_NAME"),
        'engine': 'peewee.MySQLDatabase',
        'user': os.environ.get("A2B_DB_USER"),
        'passwd': os.environ.get("A2B_DB_PASSWORD"),
    }

    DEBUG = True
    # Set the secret key.  keep this really secret
    # Default implementation stores all session data in a signed cookie. This requires that the secret_key is set
    SECRET_KEY = 'cctechsecret'
