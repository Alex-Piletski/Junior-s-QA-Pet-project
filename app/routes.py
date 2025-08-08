from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")  # Отображаем ваш HTML-файл
