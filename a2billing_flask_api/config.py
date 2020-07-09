# config
import os
import boto3

ssmclient = boto3.client('ssm')
# Function to retrieve parametsrs from AWS SSM Parameter Store
def get_secret(key):
	resp = ssmclient.get_parameter(
		Name=key,
		WithDecryption=True
	)
	return resp['Parameter']['Value']



class Configuration(object):
    # Configure your A2Billing database peewee.MySQLDatabase
    DATABASE = {
        'host': get_secret('/ans-backend-api/prod/A2B_DB_HOST'),
        'port': 3306,
        'name': get_secret('/ans-backend-api/prod/A2B_DB_NAME'),
        'engine': 'peewee.MySQLDatabase',
        'user': get_secret('/ans-backend-api/prod/A2B_DB_USER'),
        'passwd': get_secret('/ans-backend-api/prod/A2B_DB_PASSWORD),
    }

    DEBUG = True
    # Set the secret key.  keep this really secret
    # Default implementation stores all session data in a signed cookie. This requires that the secret_key is set
    SECRET_KEY = get_secret('/ans-backend-api/prod/CONFIG_SECRET_KEY')
