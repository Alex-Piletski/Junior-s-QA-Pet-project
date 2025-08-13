from app import create_app
import os

# Настройка переменных окружения для Render
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = "postgresql://flask_db_postgres_user:yi2RNn9HoOREs1US9ZH5mjXBMrvnJCx2@dpg-d2attlje5dus73c18f70-a.frankfurt-postgres.render.com/flask_db_postgres"

if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = "dev-secret-key-change-in-production"

app = create_app()

if __name__ == "__main__":
    # Указываем host и port для работы на Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

