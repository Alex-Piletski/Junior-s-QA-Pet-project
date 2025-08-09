// Валидация формы
document.getElementById('feedback-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const email = this.elements.email.value;
    if (!email.includes('@')) {
        alert('Введите корректный email');
        return;
    }
    alert('Форма отправлена!');
});

// Модальное окно
const modal = document.getElementById('modal');
const btn = document.getElementById('modal-btn');
const span = document.getElementsByClassName('close')[0];

btn.onclick = () => modal.style.display = 'block';
span.onclick = () => modal.style.display = 'none';
window.onclick = (e) => {
    if (e.target == modal) modal.style.display = 'none';
}

const registerBtn = document.getElementById('register-btn');
const loginBtn = document.getElementById('login-btn');

const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');

// Новая логика: повторное нажатие скрывает форму
registerBtn.addEventListener('click', () => {
  if (registerForm.style.display === 'flex') {
    registerForm.style.display = 'none';
  } else {
    registerForm.style.display = 'flex';
    loginForm.style.display = 'none';
  }
});

loginBtn.addEventListener('click', () => {
  if (loginForm.style.display === 'flex') {
    loginForm.style.display = 'none';
  } else {
    loginForm.style.display = 'flex';
    registerForm.style.display = 'none';
  }
});
