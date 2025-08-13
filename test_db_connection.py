import os
import psycopg2
from sqlalchemy import create_engine, inspect

# URL базы данных из Render
DATABASE_URL = "postgresql://flask_db_postgres_user:yi2RNn9HoOREs1US9ZH5mjXBMrvnJCx2@dpg-d2attlje5dus73c18f70-a.frankfurt-postgres.render.com/flask_db_postgres"

print("🔍 Тестирование подключения к PostgreSQL...")
print(f"📡 URL: {DATABASE_URL}")

try:
    # Тест прямого подключения через psycopg2
    print("\n1️⃣ Тест прямого подключения...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"📋 Таблицы в базе: {[table[0] for table in tables]}")
    
    # Если есть таблица users, показываем её структуру
    if ('users',) in tables:
        print("\n📊 Структура таблицы 'users':")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    
    cursor.close()
    conn.close()
    print("✅ Прямое подключение успешно!")
    
    # Тест через SQLAlchemy
    print("\n2️⃣ Тест через SQLAlchemy...")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables_sqlalchemy = inspector.get_table_names()
    print(f"📋 Таблицы через SQLAlchemy: {tables_sqlalchemy}")
    
    if 'users' in tables_sqlalchemy:
        print("\n📊 Структура через SQLAlchemy:")
        columns = inspector.get_columns('users')
        for column in columns:
            print(f"   - {column['name']}: {column['type']} (nullable: {column['nullable']})")
    
    print("✅ SQLAlchemy подключение успешно!")
    
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    print("\n💡 Убедитесь, что:")
    print("   1. URL базы данных правильный")
    print("   2. База данных доступна")
    print("   3. Учетные данные корректны")
