#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы приложения
"""

from wsgi import app

if __name__ == "__main__":
    print("🚀 Запуск тестового сервера...")
    print("📡 Приложение будет доступно по адресу: http://localhost:5000")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
