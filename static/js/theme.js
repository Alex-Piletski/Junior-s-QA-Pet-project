// Управление темами
class ThemeManager {
  constructor() {
    this.currentTheme = this.getStoredTheme() || "light";
    this.init();
  }

  init() {
    // Применяем сохраненную тему
    this.applyTheme(this.currentTheme);

    // Создаем переключатель темы
    this.createThemeToggle();

    // Слушаем изменения системной темы
    this.watchSystemTheme();
  }

  getStoredTheme() {
    return localStorage.getItem("theme");
  }

  setStoredTheme(theme) {
    localStorage.setItem("theme", theme);
  }

  applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    this.currentTheme = theme;
    this.setStoredTheme(theme);

    // Обновляем иконку переключателя
    this.updateToggleIcon();

    // Логируем изменение темы
    console.log(`Тема изменена на: ${theme}`);
  }

  toggleTheme() {
    const newTheme = this.currentTheme === "light" ? "dark" : "light";
    this.applyTheme(newTheme);

    // Анимация переключения
    this.animateThemeChange();
  }

  animateThemeChange() {
    // Добавляем класс для анимации
    document.body.classList.add("theme-transitioning");

    // Убираем класс через время анимации
    setTimeout(() => {
      document.body.classList.remove("theme-transitioning");
    }, 300);
  }

  createThemeToggle() {
    // Проверяем, не существует ли уже переключатель
    if (document.getElementById("theme-toggle")) {
      return;
    }

    const toggle = document.createElement("div");
    toggle.id = "theme-toggle";
    toggle.className = "theme-toggle";
    toggle.title = "Переключить тему";
    toggle.innerHTML = '<span class="icon">🌙</span>';

    toggle.addEventListener("click", () => {
      this.toggleTheme();
    });

    document.body.appendChild(toggle);
    this.updateToggleIcon();
  }

  updateToggleIcon() {
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    const icon = toggle.querySelector(".icon");
    if (this.currentTheme === "dark") {
      icon.textContent = "☀️";
      toggle.title = "Переключить на светлую тему";
    } else {
      icon.textContent = "🌙";
      toggle.title = "Переключить на тёмную тему";
    }
  }

  watchSystemTheme() {
    // Проверяем поддержку системной темы
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

      // Функция обработки изменения системной темы
      const handleSystemThemeChange = (e) => {
        // Применяем системную тему только если пользователь не выбрал тему вручную
        if (!this.getStoredTheme()) {
          const systemTheme = e.matches ? "dark" : "light";
          this.applyTheme(systemTheme);
        }
      };

      // Слушаем изменения
      mediaQuery.addEventListener("change", handleSystemThemeChange);

      // Применяем системную тему при первой загрузке (если нет сохраненной)
      if (!this.getStoredTheme()) {
        handleSystemThemeChange(mediaQuery);
      }
    }
  }

  // Метод для получения текущей темы
  getCurrentTheme() {
    return this.currentTheme;
  }

  // Метод для принудительной установки темы
  setTheme(theme) {
    if (theme === "light" || theme === "dark") {
      this.applyTheme(theme);
    }
  }
}

// Инициализация менеджера тем при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  window.themeManager = new ThemeManager();
});

// Экспорт для использования в других скриптах
if (typeof module !== "undefined" && module.exports) {
  module.exports = ThemeManager;
}
