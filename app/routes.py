
from app import app
from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")  # Убедитесь что index.html в templates/

@app.route("/ping")
def ping():
    return {"status": "ok"}
