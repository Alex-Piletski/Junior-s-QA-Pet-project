from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import os

bp = Blueprint('main', __name__)

# Папка для хранения аватарок
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/ping')
def ping():
    return {'status': 'ok'}

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Проверка данных
        if not email or not password:
            return jsonify({'error': 'Email и пароль обязательны'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Пароли не совпадают'}), 400
        
        User = current_app.User
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
        
        # Создание пользователя с базовыми данными
        user = User(
            email=email,
            first_name='Новый пользователь',
            last_name='',
            age=0,
            avatar_url='',
            role='user',
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Регистрация успешна! Теперь войдите в систему.'}), 200
    
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email и пароль обязательны'}), 400
        
        User = current_app.User
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'message': 'Вход выполнен успешно!', 'redirect': '/profile'}), 200
        else:
            return jsonify({'error': 'Неверный email или пароль'}), 400
    
    return render_template('index.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Обновляем данные профиля
        current_user.first_name = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.age = request.form.get("age")
        current_user.about = request.form.get("about")

        # Обработка аватарки
        if "avatar" in request.files:
            avatar = request.files["avatar"]
            if avatar.filename != "":
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(UPLOAD_FOLDER, filename)
                avatar.save(avatar_path)
                current_user.avatar_url = f"/{avatar_path}"

        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for("main.profile"))

    return render_template("profile.html", user=current_user)

@bp.route('/delete_avatar')
@login_required
def delete_avatar():
    if current_user.avatar_url:
        file_path = current_user.avatar_url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)
        current_user.avatar_url = ""
        db.session.commit()
        flash('Аватар удален!', 'success')
    return redirect(url_for("main.profile"))

