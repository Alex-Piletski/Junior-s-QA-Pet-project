// Обработчик ошибок на клиенте
class ErrorHandler {
  constructor() {
    this.init();
  }

  init() {
    // Обработка ошибок JavaScript
    window.addEventListener("error", (event) => {
      this.handleJavaScriptError(event.error, event.filename, event.lineno);
    });

    // Обработка необработанных промисов
    window.addEventListener("unhandledrejection", (event) => {
      this.handlePromiseError(event.reason);
    });

    // Перехват fetch запросов для обработки ошибок
    this.interceptFetch();
  }

  handleJavaScriptError(error, filename, lineno) {
    console.error("JavaScript Error:", {
      message: error?.message || "Unknown error",
      filename: filename,
      lineno: lineno,
      stack: error?.stack,
    });

    // Отправляем ошибку на сервер для логирования
    this.logErrorToServer({
      type: "javascript_error",
      message: error?.message || "Unknown error",
      filename: filename,
      lineno: lineno,
      stack: error?.stack,
      url: window.location.href,
      userAgent: navigator.userAgent,
    });

    // Показываем пользователю уведомление
    this.showErrorNotification(
      "Произошла ошибка JavaScript. Попробуйте обновить страницу."
    );
  }

  handlePromiseError(reason) {
    console.error("Unhandled Promise Rejection:", reason);

    this.logErrorToServer({
      type: "promise_error",
      message: reason?.message || String(reason),
      url: window.location.href,
      userAgent: navigator.userAgent,
    });

    this.showErrorNotification("Произошла ошибка при выполнении операции.");
  }

  interceptFetch() {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      try {
        const response = await originalFetch(...args);

        // Обрабатываем HTTP ошибки
        if (!response.ok) {
          await this.handleHttpError(response, args[0]);
        }

        return response;
      } catch (error) {
        // Обрабатываем сетевые ошибки
        this.handleNetworkError(error, args[0]);
        throw error;
      }
    };
  }

  async handleHttpError(response, url) {
    const errorInfo = {
      type: "http_error",
      status: response.status,
      statusText: response.statusText,
      url: typeof url === "string" ? url : url?.url || "unknown",
      userAgent: navigator.userAgent,
    };

    try {
      const errorData = await response.json();
      errorInfo.errorData = errorData;
    } catch (e) {
      // Если не удалось получить JSON, используем текстовый ответ
      try {
        errorInfo.errorText = await response.text();
      } catch (e2) {
        errorInfo.errorText = "Unable to read error response";
      }
    }

    this.logErrorToServer(errorInfo);

    // Показываем пользователю соответствующее сообщение
    let message = "Произошла ошибка при выполнении запроса.";

    switch (response.status) {
      case 400:
        message = "Некорректный запрос. Проверьте введенные данные.";
        break;
      case 401:
        message = "Требуется авторизация. Войдите в систему.";
        break;
      case 403:
        message =
          "Доступ запрещен. У вас нет прав для выполнения этого действия.";
        break;
      case 404:
        message = "Запрашиваемый ресурс не найден.";
        break;
      case 429:
        message = "Слишком много запросов. Попробуйте позже.";
        break;
      case 500:
        message = "Внутренняя ошибка сервера. Попробуйте позже.";
        break;
      case 502:
      case 503:
        message = "Сервис временно недоступен. Попробуйте позже.";
        break;
    }

    this.showErrorNotification(message);
  }

  handleNetworkError(error, url) {
    console.error("Network Error:", error);

    this.logErrorToServer({
      type: "network_error",
      message: error.message,
      url: typeof url === "string" ? url : url?.url || "unknown",
      userAgent: navigator.userAgent,
    });

    this.showErrorNotification(
      "Ошибка сети. Проверьте подключение к интернету."
    );
  }

  async logErrorToServer(errorInfo) {
    try {
      await fetch("/api/log-error", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...errorInfo,
          timestamp: new Date().toISOString(),
          page: window.location.href,
        }),
      });
    } catch (e) {
      // Если не удалось отправить ошибку на сервер, логируем локально
      console.error("Failed to log error to server:", e);
    }
  }

  showErrorNotification(message) {
    // Создаем уведомление об ошибке
    const notification = document.createElement("div");
    notification.className = "error-notification";
    notification.innerHTML = `
            <div class="error-notification-content">
                <span class="error-notification-icon">⚠️</span>
                <span class="error-notification-message">${message}</span>
                <button class="error-notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

    // Добавляем стили
    if (!document.getElementById("error-notification-styles")) {
      const styles = document.createElement("style");
      styles.id = "error-notification-styles";
      styles.textContent = `
                .error-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--error-bg);
                    color: var(--error-text);
                    border: 1px solid var(--error-border);
                    border-radius: 8px;
                    padding: 15px;
                    z-index: 10000;
                    max-width: 400px;
                    box-shadow: var(--shadow);
                    animation: slideIn 0.3s ease;
                }
                
                .error-notification-content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .error-notification-icon {
                    font-size: 20px;
                }
                
                .error-notification-message {
                    flex: 1;
                    font-size: 14px;
                }
                
                .error-notification-close {
                    background: none;
                    border: none;
                    color: var(--error-text);
                    font-size: 20px;
                    cursor: pointer;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .error-notification-close:hover {
                    opacity: 0.7;
                }
                
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
      document.head.appendChild(styles);
    }

    document.body.appendChild(notification);

    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }

  // Метод для ручного логирования ошибок
  logError(type, message, details = {}) {
    this.logErrorToServer({
      type: type,
      message: message,
      ...details,
      url: window.location.href,
      userAgent: navigator.userAgent,
    });
  }
}

// Инициализация обработчика ошибок при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  window.errorHandler = new ErrorHandler();
});

// Экспорт для использования в других скриптах
if (typeof module !== "undefined" && module.exports) {
  module.exports = ErrorHandler;
}
