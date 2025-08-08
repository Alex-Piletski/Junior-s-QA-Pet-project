
from app import app
from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return {"status": "ok"}
