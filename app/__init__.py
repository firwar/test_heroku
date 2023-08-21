from flask import Flask
from config import Config
from dotenv import load_dotenv
from .utils.commonly_airtable import CommonlyAirtable

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)


with app.app_context():
    app.commonly_airtable = CommonlyAirtable(app.config['AIRTABLE_API_KEY'])

from app import routes