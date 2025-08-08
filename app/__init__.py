import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# объект БД
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # URL базы данных берём из переменной окружения на Render
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # инициализируем БД в приложении
    db.init_app(app)

    # импортируем маршруты и модели
    with app.app_context():
        from app import routes, models

    return app


