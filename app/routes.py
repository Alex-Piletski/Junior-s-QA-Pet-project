from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.i18n import get_text, get_locale, set_locale, get_available_locales
from app.rate_limiter import auth_limit, api_limit, profile_limit, admin_limit, general_limit, log_rate_limit_event
from datetime import datetime
import os
import re
import html
import logging
import hashlib
import json

bp = Blueprint('main', __name__)

# Папка для хранения аватарок
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Функции безопасности
def sanitize_input(text):
    """Очистка входных данных от XSS"""
    if not text:
        return ""
    # Удаляем HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    # Экранируем специальные символы
    text = html.escape(text)
    return text.strip()

def validate_email(email):
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Валидация пароля"""
    if len(password) < 6:
        return False, get_text('password_too_short')
    return True, ""

def log_action(action, user_id=None, details=""):
    """Логирование действий пользователей"""
    if user_id is None and current_user.is_authenticated:
        user_id = current_user.id
    message = f"ACTION: {action} | USER: {user_id} | IP: {request.remote_addr} | {details}"
    current_app.logger.info(message)

def generate_etag(data):
    """Генерация ETag для данных"""
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    return hashlib.md5(data_str.encode()).hexdigest()

def check_etag(etag):
    """Проверка ETag в заголовках запроса"""
    if_none_match = request.headers.get('If-None-Match')
    return if_none_match and etag in if_none_match

@bp.route('/')
@general_limit('home')
def home():
    return render_template('index.html')

@bp.route('/ping')
@general_limit('ping')
def ping():
    return {'status': 'ok'}

@bp.route('/locale/<locale>')
@general_limit('locale')
def change_locale(locale):
    """Переключение языка"""
    if set_locale(locale):
        log_action("LOCALE_CHANGED", details=f"Changed to {locale}")
        flash(f'Язык изменен на {get_text("russian" if locale == "ru" else "english", locale)}', 'success')
    return redirect(request.referrer or url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
@auth_limit('register')
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Валидация данных
        if not email or not password:
            log_action("REGISTER_FAILED", details=f"Missing data for email: {email}")
            return jsonify({'error': get_text('email') + ' и ' + get_text('password') + ' обязательны'}), 400
        
        if not validate_email(email):
            log_action("REGISTER_FAILED", details=f"Invalid email format: {email}")
            return jsonify({'error': get_text('invalid_email')}), 400
        
        is_valid, password_error = validate_password(password)
        if not is_valid:
            log_action("REGISTER_FAILED", details=f"Invalid password for email: {email}")
            return jsonify({'error': password_error}), 400
        
        if password != confirm_password:
            log_action("REGISTER_FAILED", details=f"Password mismatch for email: {email}")
            return jsonify({'error': get_text('passwords_dont_match')}), 400
        
        User = current_app.User
        if User.query.filter_by(email=email).first():
            log_action("REGISTER_FAILED", details=f"Email already exists: {email}")
            return jsonify({'error': get_text('email_exists')}), 400
        
        # Создание пользователя с базовыми данными
        user = User(
            email=email,
            first_name=get_text('welcome'),
            last_name='',
            age=0,
            avatar_url='',
            role='user',
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        log_action("REGISTER_SUCCESS", user.id, f"New user registered: {email}")
        return jsonify({'message': get_text('register_success')}), 200
    
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
@auth_limit('login')
def login():
    if request.method == 'POST':
        data = request.get_json()
        
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        
        if not email or not password:
            log_action("LOGIN_FAILED", details=f"Missing credentials for email: {email}")
            return jsonify({'error': get_text('email') + ' и ' + get_text('password') + ' обязательны'}), 400
        
        User = current_app.User
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            log_action("LOGIN_SUCCESS", user.id, f"User logged in: {email}")
            return jsonify({'message': get_text('login_success'), 'redirect': '/profile'}), 200
        else:
            log_action("LOGIN_FAILED", details=f"Invalid credentials for email: {email}")
            return jsonify({'error': get_text('invalid_credentials')}), 400
    
    return render_template('index.html')

@bp.route('/logout')
@login_required
@auth_limit('logout')
def logout():
    user_id = current_user.id
    email = current_user.email
    logout_user()
    log_action("LOGOUT", user_id, f"User logged out: {email}")
    return redirect(url_for('main.home'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
@profile_limit('view')
def profile():
    if request.method == 'POST':
        # Обновляем данные профиля с санитизацией
        old_data = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'age': current_user.age,
            'about': current_user.about
        }
        
        current_user.first_name = sanitize_input(request.form.get("first_name", ""))
        current_user.last_name = sanitize_input(request.form.get("last_name", ""))
        
        age = request.form.get("age")
        if age:
            try:
                current_user.age = int(age)
            except ValueError:
                flash(get_text('error') + ': ' + get_text('age') + ' должен быть числом', 'error')
                log_action("PROFILE_UPDATE_FAILED", current_user.id, "Invalid age format")
                return redirect(url_for("main.profile"))
        
        current_user.about = sanitize_input(request.form.get("about", ""))

# Обработка аватарки
    avatar_uploaded = False
    if "avatar" in request.files:
        avatar = request.files["avatar"]
        if avatar.filename != "":
            # Проверяем расширение файла
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in avatar.filename and \
               avatar.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(UPLOAD_FOLDER, filename)
                avatar.save(avatar_path)
                current_user.avatar_url = f"/{avatar_path}"
                avatar_uploaded = True
            else:
                flash('Разрешены только изображения (png, jpg, jpeg, gif)', 'error')
                log_action("AVATAR_UPLOAD_FAILED", current_user.id,
                           f"Invalid file type: {avatar.filename}")

    db.session.commit()

db.session.commit()
        
        # Логируем изменения
    changes = []
    for field, old_value in old_data.items():
        new_value = getattr(current_user, field)
        if old_value != new_value:
            changes.append(f"{field}: {old_value} -> {new_value}")

    if changes:
        log_action("PROFILE_UPDATED", current_user.id, f"Changes: {', '.join(changes)}")

    if avatar_uploaded:
        log_action("AVATAR_UPLOADED", current_user.id, f"New avatar: {filename}")

    flash(get_text('profile_updated'), 'success')
    return redirect(url_for("main.profile"))

    return render_template("profile.html", user=current_user)

@bp.route('/delete_avatar')
@login_required
@profile_limit('avatar')
def delete_avatar():
    if current_user.avatar_url:
        file_path = current_user.avatar_url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)
            log_action("AVATAR_DELETED", current_user.id, f"Deleted avatar: {file_path}")
        current_user.avatar_url = ""
        db.session.commit()
        flash(get_text('delete_avatar') + ' удален!', 'success')
    return redirect(url_for("main.profile"))

# CRUD операции для заметок
@bp.route('/notes')
@login_required
@profile_limit('view')
def notes():
    return render_template('notes.html')

@bp.route('/api/notes', methods=['GET'])
@login_required
@api_limit('get_notes')
def get_notes():
    """Получение заметок с сортировкой и фильтрацией"""
    User = current_app.User
    Note = current_app.Note
    
    # Параметры запроса с санитизацией
    sort_by = sanitize_input(request.args.get('sort', 'created_at'))
    order = sanitize_input(request.args.get('order', 'desc'))
    status = sanitize_input(request.args.get('status', 'all'))
    search = sanitize_input(request.args.get('search', ''))
    
    # Валидация параметров сортировки
    allowed_sort_fields = ['created_at', 'updated_at', 'title']
    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'
    
    if order not in ['asc', 'desc']:
        order = 'desc'
    
    # Валидация статуса
    allowed_statuses = ['all', 'active', 'completed', 'archived']
    if status not in allowed_statuses:
        status = 'all'
    
    # Базовый запрос
    query = Note.query.filter_by(user_id=current_user.id)
    
    # Фильтрация по статусу
    if status != 'all':
        query = query.filter_by(status=status)
    
    # Поиск по названию и содержимому
    if search:
        query = query.filter(
            db.or_(
                Note.title.ilike(f'%{search}%'),
                Note.content.ilike(f'%{search}%')
            )
        )
    
    # Сортировка
    if hasattr(Note, sort_by):
        sort_column = getattr(Note, sort_by)
        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    notes = query.all()
    
    # Подготавливаем данные для ответа
    notes_data = [{
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'status': note.status,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    } for note in notes]
    
    # Генерируем ETag для кэширования
    etag = generate_etag(notes_data)
    
    # Проверяем, изменились ли данные
    if check_etag(etag):
        log_action("NOTES_CACHED", current_user.id, f"Returned cached data for {len(notes)} notes")
        return '', 304  # Not Modified
    
    log_action("NOTES_VIEWED", current_user.id, f"Viewed {len(notes)} notes")
    
    # Создаем ответ с заголовками кэширования
    response = make_response(jsonify(notes_data))
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'private, max-age=60'  # Кэш на 1 минуту
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return response

@bp.route('/api/notes', methods=['POST'])
@login_required
@api_limit('create_note')
def create_note():
    """Создание новой заметки"""
    data = request.get_json()
    
    title = sanitize_input(data.get('title', ''))
    content = sanitize_input(data.get('content', ''))
    status = sanitize_input(data.get('status', 'active'))
    
    if not title or not content:
        log_action("NOTE_CREATE_FAILED", current_user.id, "Missing title or content")
        return jsonify({'error': get_text('title_required') + ' и ' + get_text('content_required')}), 400
    
    if len(title) > 100:
        log_action("NOTE_CREATE_FAILED", current_user.id, "Title too long")
        return jsonify({'error': get_text('note_title') + ' не должно превышать 100 символов'}), 400
    
    if len(content) > 10000:
        log_action("NOTE_CREATE_FAILED", current_user.id, "Content too long")
        return jsonify({'error': get_text('note_content') + ' не должно превышать 10000 символов'}), 400
    
    # Валидация статуса
    allowed_statuses = ['active', 'completed', 'archived']
    if status not in allowed_statuses:
        status = 'active'
    
    Note = current_app.Note
    note = Note(
        title=title,
        content=content,
        user_id=current_user.id,
        status=status
    )
    
    db.session.add(note)
    db.session.commit()
    
    log_action("NOTE_CREATED", current_user.id, f"Created note: {title}")
    
    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'status': note.status,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    }), 201

@bp.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
@api_limit('update_note')
def update_note(note_id):
    """Обновление заметки"""
    Note = current_app.Note
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
    
    if not note:
        log_action("NOTE_UPDATE_FAILED", current_user.id, f"Note not found: {note_id}")
        return jsonify({'error': get_text('note_not_found')}), 404
    
    data = request.get_json()
    changes = []
    
    if 'title' in data:
        title = sanitize_input(data['title'])
        if not title:
            log_action("NOTE_UPDATE_FAILED", current_user.id, "Empty title")
            return jsonify({'error': get_text('title_required')}), 400
        if len(title) > 100:
            log_action("NOTE_UPDATE_FAILED", current_user.id, "Title too long")
            return jsonify({'error': get_text('note_title') + ' не должно превышать 100 символов'}), 400
        if note.title != title:
            changes.append(f"title: {note.title} -> {title}")
        note.title = title
    
    if 'content' in data:
        content = sanitize_input(data['content'])
        if not content:
            log_action("NOTE_UPDATE_FAILED", current_user.id, "Empty content")
            return jsonify({'error': get_text('content_required')}), 400
        if len(content) > 10000:
            log_action("NOTE_UPDATE_FAILED", current_user.id, "Content too long")
            return jsonify({'error': get_text('note_content') + ' не должно превышать 10000 символов'}), 400
        if note.content != content:
            changes.append(f"content: {len(note.content)} -> {len(content)} chars")
        note.content = content
    
    if 'status' in data:
        status = sanitize_input(data['status'])
        allowed_statuses = ['active', 'completed', 'archived']
        if status in allowed_statuses:
            if note.status != status:
                changes.append(f"status: {note.status} -> {status}")
            note.status = status
    
    note.updated_at = datetime.utcnow()
    db.session.commit()
    
    if changes:
        log_action("NOTE_UPDATED", current_user.id, f"Note {note_id} changes: {', '.join(changes)}")
    
    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'status': note.status,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat()
    })

@bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
@api_limit('delete_note')
def delete_note(note_id):
    """Удаление заметки"""
    Note = current_app.Note
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
    
    if not note:
        log_action("NOTE_DELETE_FAILED", current_user.id, f"Note not found: {note_id}")
        return jsonify({'error': get_text('note_not_found')}), 404
    
    title = note.title
    db.session.delete(note)
    db.session.commit()
    
    log_action("NOTE_DELETED", current_user.id, f"Deleted note: {title}")
    
    return jsonify({'message': get_text('note_deleted')}), 200

# Административные функции
@bp.route('/admin/logs')
@login_required
@admin_limit('logs')
def download_logs():
    """Скачивание логов (только для админов)"""
    if current_user.role != 'admin':
        log_action("UNAUTHORIZED_ACCESS", current_user.id, "Attempted to access logs")
        flash(get_text('access_denied'), 'error')
        return redirect(url_for('main.home'))
    
    log_file = 'logs/app.log'
    if os.path.exists(log_file):
        log_action("LOGS_DOWNLOADED", current_user.id, "Downloaded application logs")
        return send_file(log_file, as_attachment=True, download_name='app.log')
    else:
        flash('Файл логов не найден', 'error')
        return redirect(url_for('main.home'))

@bp.route('/admin/rate-limits')
@login_required
@admin_limit('logs')
def rate_limit_info():
    """Информация о rate limiting (только для админов)"""
    if current_user.role != 'admin':
        log_action("UNAUTHORIZED_ACCESS", current_user.id, "Attempted to access rate limit info")
        flash(get_text('access_denied'), 'error')
        return redirect(url_for('main.home'))
    
    log_action("RATE_LIMIT_INFO_VIEWED", current_user.id, "Viewed rate limiting information")
    return render_template('rate_limit_info.html')

@bp.route('/api/log-error', methods=['POST'])
def log_client_error():
    """Логирование ошибок с клиента"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Логируем ошибку клиента
        error_message = f"CLIENT_ERROR: {data.get('type', 'unknown')} | "
        error_message += f"Message: {data.get('message', 'No message')} | "
        error_message += f"URL: {data.get('url', 'unknown')} | "
        error_message += f"Page: {data.get('page', 'unknown')} | "
        error_message += f"User-Agent: {data.get('userAgent', 'unknown')} | "
        error_message += f"IP: {request.remote_addr}"
        
        if data.get('filename'):
            error_message += f" | File: {data.get('filename')}:{data.get('lineno', '?')}"
        
        if data.get('stack'):
            error_message += f" | Stack: {data.get('stack')[:200]}..."
        
        current_app.logger.error(error_message)
        
        return jsonify({'status': 'logged'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error logging client error: {e}")
        return jsonify({'error': 'Failed to log error'}), 500

# Маршрут для страницы мониторинга производительности
@bp.route('/performance')
@login_required
@admin_limit('logs')
def performance_monitor():
    """Страница мониторинга производительности (только для админов)"""
    if current_user.role != 'admin':
        log_action("UNAUTHORIZED_ACCESS", current_user.id, "Attempted to access performance monitor")
        flash(get_text('access_denied'), 'error')
        return redirect(url_for('main.home'))
    
    log_action("PERFORMANCE_MONITOR_VIEWED", current_user.id, "Viewed performance monitor")
    return render_template('performance_monitor.html')

# API для получения общей статистики производительности
@bp.route('/api/performance')
@login_required
@admin_limit('logs')
def get_performance_stats():
    """API для получения статистики производительности"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Простая статистика (в реальном приложении здесь была бы более сложная логика)
        import time
        from datetime import datetime, timedelta
        
        # Время работы приложения (примерно)
        start_time = datetime.now() - timedelta(hours=2)  # Пример
        uptime = datetime.now() - start_time
        uptime_str = f"{uptime.days}д {uptime.seconds // 3600}ч {(uptime.seconds % 3600) // 60}м"
        
        # Статистика запросов (пример)
        stats = {
            'uptime': uptime_str,
            'requests_per_sec': '12.5',
            'avg_response_time': '45.2мс',
            'error_rate': '0.8%'
        }
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance stats: {e}")
        return jsonify({'error': 'Failed to get performance stats'}), 500

# API для получения статистики эндпоинтов
@bp.route('/api/endpoints-performance')
@login_required
@admin_limit('logs')
def get_endpoints_performance():
    """API для получения статистики эндпоинтов"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Пример данных (в реальном приложении здесь была бы реальная статистика)
        endpoints = [
            {
                'name': 'Главная страница',
                'avg_response_time': 25.3,
                'requests_per_sec': 15.2,
                'success_rate': 99.8,
                'total_requests': 1250
            },
            {
                'name': 'API Notes',
                'avg_response_time': 45.7,
                'requests_per_sec': 8.9,
                'success_rate': 98.5,
                'total_requests': 890
            },
            {
                'name': 'Ping',
                'avg_response_time': 12.1,
                'requests_per_sec': 25.6,
                'success_rate': 100.0,
                'total_requests': 2560
            },
            {
                'name': 'Регистрация',
                'avg_response_time': 78.4,
                'requests_per_sec': 2.3,
                'success_rate': 95.2,
                'total_requests': 230
            }
        ]
        
        return jsonify({'endpoints': endpoints})
        
    except Exception as e:
        current_app.logger.error(f"Error getting endpoints performance: {e}")
        return jsonify({'error': 'Failed to get endpoints performance'}), 500

# API для нагрузочного тестирования
@bp.route('/api/load-test', methods=['POST'])
@login_required
@admin_limit('logs')
def run_load_test():
    """API для запуска нагрузочного тестирования"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        endpoint = data.get('endpoint', '/')
        concurrent_users = min(data.get('concurrent_users', 5), 50)  # Ограничиваем
        requests_per_user = min(data.get('requests_per_user', 10), 100)  # Ограничиваем
        
        # Логируем запуск теста
        log_action("LOAD_TEST_STARTED", current_user.id, 
                  f"Load test: {endpoint}, users: {concurrent_users}, requests: {requests_per_user}")
        
        # Имитируем нагрузочное тестирование
        import time
        import random
        import statistics
        
        results = []
        response_times = []
        
        # Симулируем запросы
        for user in range(concurrent_users):
            for req in range(requests_per_user):
                # Имитируем время ответа
                response_time = random.uniform(20, 200)  # 20-200мс
                response_times.append(response_time)
                
                # Имитируем успешность
                success = random.random() > 0.05  # 95% успешность
                
                results.append({
                    'response_time': response_time,
                    'success': success,
                    'size': random.randint(500, 5000)
                })
        
        # Анализируем результаты
        successful = [r for r in results if r['success']]
        total = len(results)
        
        if successful:
            avg_response_time = statistics.mean([r['response_time'] for r in successful])
            avg_response_size = statistics.mean([r['size'] for r in successful])
        else:
            avg_response_time = 0
            avg_response_size = 0
        
        success_rate = (len(successful) / total) * 100 if total > 0 else 0
        
        # Имитируем RPS
        total_time = max(response_times) / 1000  # в секундах
        requests_per_sec = total / total_time if total_time > 0 else 0
        
        # Логируем результаты
        log_action("LOAD_TEST_COMPLETED", current_user.id, 
                  f"Results: {len(successful)}/{total} successful, avg time: {avg_response_time:.2f}ms")
        
        return jsonify({
            'successful': len(successful),
            'total': total,
            'success_rate': round(success_rate, 1),
            'avg_response_time': round(avg_response_time, 1),
            'requests_per_sec': round(requests_per_sec, 1),
            'avg_response_size': round(avg_response_size, 0),
            'response_times': [round(t, 1) for t in response_times]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error running load test: {e}")
        return jsonify({'error': 'Failed to run load test'}), 500

