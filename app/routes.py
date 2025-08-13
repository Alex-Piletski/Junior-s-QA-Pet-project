from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/ping')
def ping():
    return {'status': 'ok'}

import os
from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User

# Папка для хранения аватарок
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = User.query.first()  # пока один тестовый пользователь

    if request.method == "POST":
        # Обновляем данные профиля
        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        user.age = request.form.get("age")
        user.about = request.form.get("about")

        # Обработка аватарки
        if "avatar" in request.files:
            avatar = request.files["avatar"]
            if avatar.filename != "":
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                avatar.save(avatar_path)
                user.avatar_url = f"/{avatar_path}"

        db.session.commit()
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

@app.route("/delete_avatar")
def delete_avatar():
    user = User.query.first()
    if user and user.avatar_url:
        file_path = user.avatar_url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)
        user.avatar_url = None
        db.session.commit()
    return redirect(url_for("profile"))

