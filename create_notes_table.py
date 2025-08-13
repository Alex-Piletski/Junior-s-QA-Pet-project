import psycopg2
from sqlalchemy import create_engine, text

# URL базы данных из Render
DATABASE_URL = "postgresql://flask_db_postgres_user:yi2RNn9HoOREs1US9ZH5mjXBMrvnJCx2@dpg-d2attlje5dus73c18f70-a.frankfurt-postgres.render.com/flask_db_postgres"

print("🔧 Создание таблицы notes...")

try:
    # Подключение через SQLAlchemy
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Проверяем, существует ли таблица notes
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'notes'
        """))
        
        if result.fetchone():
            print("✅ Таблица notes уже существует")
        else:
            print("➕ Создаем таблицу notes...")
            conn.execute(text("""
                CREATE TABLE notes (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    status VARCHAR(20) DEFAULT 'active'
                )
            """))
            print("✅ Таблица notes создана")
        
        conn.commit()
        
        # Показываем структуру таблицы
        print("\n📊 Структура таблицы notes:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'notes'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            print(f"   - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        print("\n🎉 Миграция завершена успешно!")
        
except Exception as e:
    print(f"❌ Ошибка при миграции: {e}")
