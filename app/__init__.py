from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import os
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__,
        template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
        static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    )

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    db_url = os.getenv('DATABASE_URL', 'sqlite:///temp.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Приложение запущено')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Инициализация rate limiting
    from .rate_limiter import limiter, rate_limit_exceeded_handler
    limiter.init_app(app)
    
    # Регистрируем обработчик превышения лимитов
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return rate_limit_exceeded_handler(e)

    # Инициализация обработчиков ошибок
    from .error_handlers import init_error_handlers
    init_error_handlers(app)

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
            email = db.Column(db.String(120), unique=True, nullable=True)
            password_hash = db.Column(db.String(255), nullable=True)
            def __repr__(self):
                return f"<User {self.first_name} {self.last_name}>"

        class NoteModel(db.Model):
            __tablename__ = 'notes'
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(100), nullable=False)
            content = db.Column(db.Text, nullable=False)
            created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
            updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
            user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            status = db.Column(db.String(20), default='active')
            def __repr__(self):
                return f"<Note {self.title}>"

        app.User = UserModel
        app.Note = NoteModel

        @login_manager.user_loader
        def load_user(user_id):
            return UserModel.query.get(int(user_id))

    from .routes import bp
    app.register_blueprint(bp)

    return app
