# Система обработки ошибок
from flask import render_template, request, jsonify, current_app
from werkzeug.exceptions import HTTPException
import traceback
import logging
from datetime import datetime

def init_error_handlers(app):
    """Инициализация обработчиков ошибок"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Обработка ошибки 400 - Bad Request"""
        return handle_error(400, "Некорректный запрос", 
                          "Запрос содержит ошибки или неверные данные", error)
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Обработка ошибки 401 - Unauthorized"""
        return handle_error(401, "Не авторизован", 
                          "Для доступа к этой странице требуется авторизация", error)
    
    @app.errorhandler(403)
    def forbidden(error):
        """Обработка ошибки 403 - Forbidden"""
        return handle_error(403, "Доступ запрещен", 
                          "У вас нет прав для доступа к этому ресурсу", error)
    
    @app.errorhandler(404)
    def not_found(error):
        """Обработка ошибки 404 - Not Found"""
        return handle_error(404, "Страница не найдена", 
                          "Запрашиваемая страница не существует", error)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Обработка ошибки 405 - Method Not Allowed"""
        return handle_error(405, "Метод не разрешен", 
                          "Данный HTTP метод не поддерживается для этого ресурса", error)
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Обработка ошибки 429 - Too Many Requests"""
        return handle_error(429, "Слишком много запросов", 
                          "Превышен лимит запросов. Попробуйте позже.", error)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Обработка ошибки 500 - Internal Server Error"""
        return handle_error(500, "Внутренняя ошибка сервера", 
                          "Произошла непредвиденная ошибка. Попробуйте позже.", error)
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Обработка ошибки 502 - Bad Gateway"""
        return handle_error(502, "Ошибка шлюза", 
                          "Проблема с подключением к внешнему сервису", error)
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Обработка ошибки 503 - Service Unavailable"""
        return handle_error(503, "Сервис недоступен", 
                          "Сервис временно недоступен. Попробуйте позже.", error)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Обработка всех остальных исключений"""
        # Логируем ошибку
        current_app.logger.error(f"Unhandled exception: {error}")
        current_app.logger.error(traceback.format_exc())
        
        return handle_error(500, "Непредвиденная ошибка", 
                          "Произошла непредвиденная ошибка. Попробуйте позже.", error)

def handle_error(status_code, title, message, error=None):
    """Универсальный обработчик ошибок"""
    
    # Логируем ошибку
    log_error(status_code, title, message, error)
    
    # Определяем, какой тип ответа ожидает клиент
    if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'error': title,
            'message': message,
            'status_code': status_code,
            'path': request.path
        }), status_code
    
    # Для обычных страниц возвращаем HTML
    return render_template('error.html', 
                         status_code=status_code,
                         title=title,
                         message=message,
                         error=error), status_code

def log_error(status_code, title, message, error=None):
    """Логирование ошибок"""
    error_info = {
        'status_code': status_code,
        'title': title,
        'message': message,
        'path': request.path,
        'method': request.method,
        'ip': get_client_ip(),
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referrer': request.headers.get('Referer', 'Unknown')
    }
    
    if error:
        error_info['error_type'] = type(error).__name__
        error_info['error_message'] = str(error)
    
    # Логируем в зависимости от типа ошибки
    if status_code >= 500:
        current_app.logger.error(f"Server Error: {error_info}")
    elif status_code >= 400:
        current_app.logger.warning(f"Client Error: {error_info}")
    else:
        current_app.logger.info(f"Info: {error_info}")

def get_client_ip():
    """Получение IP адреса клиента"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def create_error_response(status_code, message, details=None):
    """Создание стандартизированного ответа с ошибкой"""
    response = {
        'error': True,
        'status_code': status_code,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code
