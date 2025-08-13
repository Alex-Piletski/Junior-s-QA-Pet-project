from app import create_app

app = create_app()

if __name__ == "__main__":
    # Указываем host и port для работы на Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

