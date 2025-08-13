# Система ограничения запросов
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, jsonify
import time

# Создаем экземпляр лимитера
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def get_client_ip():
    """Получение IP адреса клиента"""
    # Проверяем заголовки прокси
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_user_identifier():
    """Получение идентификатора пользователя для rate limiting"""
    from flask_login import current_user
    
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    else:
        return f"ip:{get_client_ip()}"

# Настройки лимитов для разных эндпоинтов
RATE_LIMITS = {
    # Аутентификация
    'auth': {
        'login': "5 per minute",      # 5 попыток входа в минуту
        'register': "3 per hour",     # 3 регистрации в час
        'logout': "10 per minute"     # 10 выходов в минуту
    },
    
    # API заметок
    'api': {
        'get_notes': "30 per minute",     # 30 запросов списка в минуту
        'create_note': "10 per minute",   # 10 созданий в минуту
        'update_note': "20 per minute",   # 20 обновлений в минуту
        'delete_note': "5 per minute"     # 5 удалений в минуту
    },
    
    # Профиль
    'profile': {
        'view': "20 per minute",      # 20 просмотров в минуту
        'update': "5 per minute",     # 5 обновлений в минуту
        'avatar': "3 per minute"      # 3 загрузки аватара в минуту
    },
    
    # Административные функции
    'admin': {
        'logs': "2 per hour"          # 2 скачивания логов в час
    },
    
    # Общие
    'general': {
        'home': "100 per minute",     # 100 запросов главной в минуту
        'ping': "1000 per hour",      # 1000 пингов в час
        'locale': "10 per minute"     # 10 смен языка в минуту
    }
}

def get_rate_limit(endpoint_type, endpoint_name):
    """Получение лимита для конкретного эндпоинта"""
    return RATE_LIMITS.get(endpoint_type, {}).get(endpoint_name, "50 per hour")

def rate_limit_exceeded_handler(e):
    """Обработчик превышения лимита запросов"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Слишком много запросов. Попробуйте позже.',
        'retry_after': e.retry_after if hasattr(e, 'retry_after') else 60
    }), 429

def get_remaining_requests():
    """Получение информации о оставшихся запросах"""
    from flask import current_app
    
    try:
        # Получаем информацию о лимитах для текущего запроса
        endpoint = request.endpoint
        identifier = get_user_identifier()
        
        # Это упрощенная версия - в реальности нужно получить данные из лимитера
        return {
            'remaining': 'unknown',
            'limit': 'unknown',
            'reset_time': 'unknown'
        }
    except Exception:
        return {
            'remaining': 'unknown',
            'limit': 'unknown',
            'reset_time': 'unknown'
        }

def log_rate_limit_event(identifier, endpoint, action="request"):
    """Логирование событий rate limiting"""
    from flask import current_app
    
    message = f"RATE_LIMIT: {action} | IDENTIFIER: {identifier} | ENDPOINT: {endpoint} | IP: {get_client_ip()}"
    current_app.logger.info(message)

# Декораторы для удобного применения лимитов
def auth_limit(endpoint_name):
    """Декоратор для лимитов аутентификации"""
    limit = get_rate_limit('auth', endpoint_name)
    return limiter.limit(limit)

def api_limit(endpoint_name):
    """Декоратор для лимитов API"""
    limit = get_rate_limit('api', endpoint_name)
    return limiter.limit(limit)

def profile_limit(endpoint_name):
    """Декоратор для лимитов профиля"""
    limit = get_rate_limit('profile', endpoint_name)
    return limiter.limit(limit)

def admin_limit(endpoint_name):
    """Декоратор для лимитов админки"""
    limit = get_rate_limit('admin', endpoint_name)
    return limiter.limit(limit)

def general_limit(endpoint_name):
    """Декоратор для общих лимитов"""
    limit = get_rate_limit('general', endpoint_name)
    return limiter.limit(limit)
