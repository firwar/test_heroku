import os

class Config(object):
    AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DB_NAME = os.environ.get('POSTGRES_DB_NAME')
    PAPERFORM_USERNAME = os.environ.get('PAPERFORM_USERNAME')
    PAPERFORM_PASSWORD = os.environ.get('PAPERFORM_PASSWORD')
    FLASK_ENV = os.environ.get('FLASK_ENV')


class ProductionConfig(Config):
    #AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY_PROD')
    pass
