from flask import Flask

app = Flask(__name__)

# Импорт роутов ПОСЛЕ создания app
from app import routes
