from app import app  # Теперь это безопасно

@app.route('/ping')
def ping():
    return {"status": "ok"}
