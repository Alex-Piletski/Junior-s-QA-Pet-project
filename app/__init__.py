
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Подключение к PostgreSQ
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql://flask_db_postgres_user:yi2RNn9HoOREs1US9ZH5mjXBMrvnJCx2@"
    "dpg-d2attlje5dus73c18f70-a:5432/flask_db_postgres"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
