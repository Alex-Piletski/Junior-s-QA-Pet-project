from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Ваши текущие настройки БД
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host/db'
    
    db.init_app(app)
    
    # Импорт моделей после инициализации db
    from app import models
    
    return app
