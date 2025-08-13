import psycopg2
from sqlalchemy import create_engine, text

# URL базы данных из Render
DATABASE_URL = "postgresql://flask_db_postgres_user:yi2RNn9HoOREs1US9ZH5mjXBMrvnJCx2@dpg-d2attlje5dus73c18f70-a.frankfurt-postgres.render.com/flask_db_postgres"

print("🔧 Добавление полей авторизации в таблицу users...")

try:
    # Подключение через SQLAlchemy
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Проверяем, существуют ли уже поля email и password_hash
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('email', 'password_hash')
        """))
        
        existing_columns = [row[0] for row in result]
        print(f"📋 Существующие поля авторизации: {existing_columns}")
        
        # Добавляем поле email, если его нет
        if 'email' not in existing_columns:
            print("➕ Добавляем поле email...")
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120) UNIQUE"))
            print("✅ Поле email добавлено")
        else:
            print("✅ Поле email уже существует")
        
        # Добавляем поле password_hash, если его нет
        if 'password_hash' not in existing_columns:
            print("➕ Добавляем поле password_hash...")
            conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
            print("✅ Поле password_hash добавлено")
        else:
            print("✅ Поле password_hash уже существует")
        
        conn.commit()
        
        # Показываем финальную структуру
        print("\n📊 Финальная структура таблицы users:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            print(f"   - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        print("\n🎉 Миграция завершена успешно!")
        
except Exception as e:
    print(f"❌ Ошибка при миграции: {e}")
