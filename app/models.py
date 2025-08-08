from app import db

# Пример заготовки (пока не создаёт таблицы в БД)
class User(db.Model):
    """Шаблон для таблицы пользователей"""
    __tablename__ = 'users'  # Это имя таблицы в БД
    
    # Поля будут добавлены позже
    pass

class Product(db.Model):
    """Шаблон для таблицы товаров"""
    __tablename__ = 'products'
    pass
