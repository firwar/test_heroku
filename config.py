import os

class Config(object):
    AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')