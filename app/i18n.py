# Система локализации
from flask import request, session

# Словари переводов
TRANSLATIONS = {
    'ru': {
        'welcome': 'Добро пожаловать',
        'loading': 'Загрузка...',
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'delete': 'Удалить',
        'edit': 'Редактировать',
        'create': 'Создать',
        'update': 'Обновить',
        'back': 'Назад',
        'close': 'Закрыть',
        'confirm': 'Подтвердить',
        'error': 'Ошибка',
        'success': 'Успешно',
        'warning': 'Предупреждение',
        'info': 'Информация',
        
        # Навигация
        'home': 'Главная',
        'profile': 'Профиль',
        'notes': 'Заметки',
        'logout': 'Выйти',
        'login': 'Войти',
        'register': 'Регистрация',
        
        # Аутентификация
        'email': 'Email',
        'password': 'Пароль',
        'confirm_password': 'Подтвердите пароль',
        'username': 'Имя пользователя',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'age': 'Возраст',
        'about': 'О себе',
        'role': 'Роль',
        'avatar': 'Аватар',
        'upload_avatar': 'Загрузить аватар',
        'delete_avatar': 'Удалить аватар',
        
        # Сообщения
        'login_success': 'Вход выполнен успешно!',
        'register_success': 'Регистрация успешна! Теперь войдите в систему.',
        'profile_updated': 'Профиль обновлен!',
        'note_created': 'Заметка создана!',
        'note_updated': 'Заметка обновлена!',
        'note_deleted': 'Заметка удалена!',
        'cache_cleared': 'Кэш очищен!',
        
        # Ошибки
        'invalid_email': 'Некорректный формат email',
        'password_too_short': 'Пароль должен содержать минимум 6 символов',
        'passwords_dont_match': 'Пароли не совпадают',
        'email_exists': 'Пользователь с таким email уже существует',
        'invalid_credentials': 'Неверный email или пароль',
        'access_denied': 'Доступ запрещен',
        'note_not_found': 'Заметка не найдена',
        'title_required': 'Название обязательно',
        'content_required': 'Содержимое обязательно',
        
        # Заметки
        'my_notes': 'Мои заметки',
        'new_note': 'Новая заметка',
        'edit_note': 'Редактировать заметку',
        'note_title': 'Название',
        'note_content': 'Содержимое',
        'note_status': 'Статус',
        'search_notes': 'Поиск по заметкам...',
        'all_statuses': 'Все статусы',
        'active': 'Активные',
        'completed': 'Завершенные',
        'archived': 'Архивные',
        'no_notes_found': 'Заметок не найдено',
        'delete_note_confirm': 'Вы уверены, что хотите удалить эту заметку?',
        
        # Кэширование
        'cache_loaded': 'Данные загружены из кэша',
        'cache_not_modified': 'Данные не изменились (кэш)',
        'cache_saved': 'Данные сохранены в кэш',
        
        # Темы
        'theme_system': 'Система тем',
        'theme_info': 'Приложение поддерживает светлую и тёмную темы.',
        'switch_to_light': 'Переключить на светлую тему',
        'switch_to_dark': 'Переключить на тёмную тему',
        
        # Локализация
        'language': 'Язык',
        'russian': 'Русский',
        'english': 'English',
        'switch_language': 'Переключить язык',
        
        # Обратная связь
        'feedback': 'Обратная связь',
        'feedback_name': 'Имя',
        'feedback_message': 'Сообщение',
        'send_feedback': 'Отправить',
        'open_modal': 'Открыть модальное окно'
    },
    
    'en': {
        'welcome': 'Welcome',
        'loading': 'Loading...',
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'create': 'Create',
        'update': 'Update',
        'back': 'Back',
        'close': 'Close',
        'confirm': 'Confirm',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Information',
        
        # Navigation
        'home': 'Home',
        'profile': 'Profile',
        'notes': 'Notes',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',
        
        # Authentication
        'email': 'Email',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'username': 'Username',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'age': 'Age',
        'about': 'About',
        'role': 'Role',
        'avatar': 'Avatar',
        'upload_avatar': 'Upload Avatar',
        'delete_avatar': 'Delete Avatar',
        
        # Messages
        'login_success': 'Login successful!',
        'register_success': 'Registration successful! Now log in.',
        'profile_updated': 'Profile updated!',
        'note_created': 'Note created!',
        'note_updated': 'Note updated!',
        'note_deleted': 'Note deleted!',
        'cache_cleared': 'Cache cleared!',
        
        # Errors
        'invalid_email': 'Invalid email format',
        'password_too_short': 'Password must be at least 6 characters',
        'passwords_dont_match': 'Passwords do not match',
        'email_exists': 'User with this email already exists',
        'invalid_credentials': 'Invalid email or password',
        'access_denied': 'Access denied',
        'note_not_found': 'Note not found',
        'title_required': 'Title is required',
        'content_required': 'Content is required',
        
        # Notes
        'my_notes': 'My Notes',
        'new_note': 'New Note',
        'edit_note': 'Edit Note',
        'note_title': 'Title',
        'note_content': 'Content',
        'note_status': 'Status',
        'search_notes': 'Search notes...',
        'all_statuses': 'All Statuses',
        'active': 'Active',
        'completed': 'Completed',
        'archived': 'Archived',
        'no_notes_found': 'No notes found',
        'delete_note_confirm': 'Are you sure you want to delete this note?',
        
        # Caching
        'cache_loaded': 'Data loaded from cache',
        'cache_not_modified': 'Data not modified (cache)',
        'cache_saved': 'Data saved to cache',
        
        # Themes
        'theme_system': 'Theme System',
        'theme_info': 'The application supports light and dark themes.',
        'switch_to_light': 'Switch to light theme',
        'switch_to_dark': 'Switch to dark theme',
        
        # Localization
        'language': 'Language',
        'russian': 'Русский',
        'english': 'English',
        'switch_language': 'Switch language',
        
        # Feedback
        'feedback': 'Feedback',
        'feedback_name': 'Name',
        'feedback_message': 'Message',
        'send_feedback': 'Send',
        'open_modal': 'Open Modal Window'
    }
}

def get_locale():
    """Получение текущей локали"""
    if 'locale' in session:
        return session['locale']
    
    accept_language = request.headers.get('Accept-Language', '')
    if 'ru' in accept_language.lower():
        return 'ru'
    elif 'en' in accept_language.lower():
        return 'en'
    
    return 'ru'

def set_locale(locale):
    """Установка локали"""
    if locale in TRANSLATIONS:
        session['locale'] = locale
        return True
    return False

def get_text(key, locale=None):
    """Получение перевода по ключу"""
    if locale is None:
        locale = get_locale()
    
    return TRANSLATIONS.get(locale, TRANSLATIONS['ru']).get(key, key)

def get_available_locales():
    """Получение списка доступных локалей"""
    return list(TRANSLATIONS.keys())

def get_locale_name(locale):
    """Получение названия локали"""
    locale_names = {
        'ru': 'Русский',
        'en': 'English'
    }
    return locale_names.get(locale, locale)
