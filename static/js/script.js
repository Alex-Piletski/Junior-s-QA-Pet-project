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
