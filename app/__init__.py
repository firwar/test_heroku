from flask import Flask
from config import Config
from dotenv import load_dotenv
from .utils.commonly_airtable import CommonlyAirtable
from .utils.commonly_postgres import CommonlyPostgres
from .utils.commonly_paperform import CommonlyPaperform

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    app.commonly_airtable = CommonlyAirtable(app.config['AIRTABLE_API_KEY'], app.config['FLASK_ENV'])
    app.commonly_postgres = CommonlyPostgres(app.config['POSTGRES_HOST'], app.config['POSTGRES_PASSWORD'], app.config['POSTGRES_DB_NAME'])
    app.commonly_paperform = CommonlyPaperform(app.config['PAPERFORM_USERNAME'], app.config['PAPERFORM_PASSWORD'])

from app import routes