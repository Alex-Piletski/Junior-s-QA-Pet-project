// Валидация формы обратной связи
document
  .getElementById("feedback-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    const email = this.elements.email.value;
    if (!email.includes("@")) {
      alert("Введите корректный email");
      return;
    }
    alert("Форма отправлена!");
  });

// Модальное окно
const modal = document.getElementById("modal");
const btn = document.getElementById("modal-btn");
const span = document.getElementsByClassName("close")[0];

btn.onclick = () => (modal.style.display = "block");
span.onclick = () => (modal.style.display = "none");
window.onclick = (e) => {
  if (e.target == modal) modal.style.display = "none";
};

// Кнопки и формы авторизации
const registerBtn = document.getElementById("register-btn");
const loginBtn = document.getElementById("login-btn");
const registerForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");

// Показать/скрыть формы
registerBtn.addEventListener("click", () => {
  if (registerForm.style.display === "flex") {
    registerForm.style.display = "none";
  } else {
    registerForm.style.display = "flex";
    loginForm.style.display = "none";
  }
});

loginBtn.addEventListener("click", () => {
  if (loginForm.style.display === "flex") {
    loginForm.style.display = "none";
  } else {
    loginForm.style.display = "flex";
    registerForm.style.display = "none";
  }
});

// Обработка регистрации
registerForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const formData = {
    email: this.elements.email.value,
    password: this.elements.password.value,
    confirm_password: this.elements.confirm_password.value,
  };

  fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Ошибка: " + data.error);
      } else {
        alert(data.message);
        registerForm.style.display = "none";
        registerForm.reset();
      }
    })
    .catch((error) => {
      console.error("Ошибка:", error);
      alert("Произошла ошибка при регистрации");
    });
});

// Обработка авторизации
loginForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const formData = {
    email: this.elements.email.value,
    password: this.elements.password.value,
  };

  fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Ошибка: " + data.error);
      } else {
        alert(data.message);
        loginForm.style.display = "none";
        loginForm.reset();
        if (data.redirect) {
          window.location.href = data.redirect;
        }
      }
    })
    .catch((error) => {
      console.error("Ошибка:", error);
      alert("Произошла ошибка при входе");
    });
});
