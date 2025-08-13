from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__,
        template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
        static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    )

    # Секретный ключ для сессий
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    db_url = os.getenv('DATABASE_URL', 'sqlite:///temp.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Инициализируем модель User
    with app.app_context():
        class UserModel(db.Model, UserMixin):
            __tablename__ = 'users'

            id = db.Column(db.Integer, primary_key=True)
            first_name = db.Column(db.String(50), nullable=False)
            last_name = db.Column(db.String(50), nullable=False)
            age = db.Column(db.Integer, nullable=False)
            avatar_url = db.Column(db.Text, nullable=False)
            about = db.Column(db.String(300))
            role = db.Column(db.String(20), nullable=False)
            
            # Поля для авторизации
            email = db.Column(db.String(120), unique=True, nullable=True)
            password_hash = db.Column(db.String(255), nullable=True)

            def __repr__(self):
                return f"<User {self.first_name} {self.last_name}>"

        # Создаем глобальную переменную User
        app.User = UserModel

        @login_manager.user_loader
        def load_user(user_id):
            return UserModel.query.get(int(user_id))

    from .routes import bp
    app.register_blueprint(bp)

    return app
