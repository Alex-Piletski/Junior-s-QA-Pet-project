// Управление локализацией
class LocaleManager {
    constructor() {
        this.currentLocale = this.getStoredLocale() || 'ru';
        this.init();
    }

    init() {
        // Создаем переключатель языка
        this.createLocaleToggle();
        
        // Применяем текущую локаль
        this.applyLocale(this.currentLocale);
    }

    getStoredLocale() {
        return localStorage.getItem('locale') || 'ru';
    }

    setStoredLocale(locale) {
        localStorage.setItem('locale', locale);
    }

    applyLocale(locale) {
        this.currentLocale = locale;
        this.setStoredLocale(locale);
        
        // Обновляем иконку переключателя
        this.updateToggleIcon();
        
        // Логируем изменение языка
        console.log(`Язык изменен на: ${locale}`);
    }

    changeLocale(locale) {
        if (locale === 'ru' || locale === 'en') {
            // Переходим на страницу смены языка
            window.location.href = `/locale/${locale}`;
        }
    }

    createLocaleToggle() {
        // Проверяем, не существует ли уже переключатель
        if (document.getElementById('locale-toggle')) {
            return;
        }

        const toggle = document.createElement('div');
        toggle.id = 'locale-toggle';
        toggle.className = 'locale-toggle';
        toggle.title = 'Переключить язык';
        toggle.innerHTML = '<span class="icon">🇷🇺</span>';
        
        toggle.addEventListener('click', () => {
            const newLocale = this.currentLocale === 'ru' ? 'en' : 'ru';
            this.changeLocale(newLocale);
        });

        document.body.appendChild(toggle);
        this.updateToggleIcon();
    }

    updateToggleIcon() {
        const toggle = document.getElementById('locale-toggle');
        if (!toggle) return;

        const icon = toggle.querySelector('.icon');
        if (this.currentLocale === 'en') {
            icon.textContent = '🇺🇸';
            toggle.title = 'Switch to Russian';
        } else {
            icon.textContent = '🇷🇺';
            toggle.title = 'Switch to English';
        }
    }

    // Метод для получения текущей локали
    getCurrentLocale() {
        return this.currentLocale;
    }

    // Метод для принудительной установки локали
    setLocale(locale) {
        if (locale === 'ru' || locale === 'en') {
            this.changeLocale(locale);
        }
    }
}

// Инициализация менеджера локализации при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.localeManager = new LocaleManager();
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LocaleManager;
}
