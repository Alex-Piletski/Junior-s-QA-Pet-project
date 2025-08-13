from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Таблицы созданы!")
    print("📋 Структура таблицы users:")
    print("   - id (Integer, Primary Key)")
    print("   - email (String, Unique, Not Null)")
    print("   - password_hash (String, Not Null)")
    print("   - first_name (String)")
    print("   - last_name (String)")
    print("   - age (Integer)")
    print("   - about (Text)")
    print("   - avatar (String)")
