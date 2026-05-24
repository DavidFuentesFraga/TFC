const API_BASE = 'http://127.0.0.1:8000/api';

function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Token ${token}`;
    return headers;
}

function actualizarMenu() {
    const token = localStorage.getItem('auth_token');
    const menu = document.getElementById('menu-links');
    if (!menu) return;

    // Limpiar posibles enlaces dinámicos anteriores
    const oldUser = document.getElementById('user-info');
    if (oldUser) oldUser.remove();
    const oldCartLink = document.getElementById('cart-link');
    if (oldCartLink) oldCartLink.remove();

    if (token) {
        const username = localStorage.getItem('username');
        const userSpan = document.createElement('span');
        userSpan.id = 'user-info';
        userSpan.style.cssText = 'color:#00ff88; margin-left:20px;';
        userSpan.textContent = `Hola, ${username}`;
        menu.appendChild(userSpan);

        const logoutLink = document.createElement('a');
        logoutLink.href = '#';
        logoutLink.textContent = 'Salir';
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('auth_token');
            localStorage.removeItem('username');
            window.location.reload();
        });
        menu.appendChild(logoutLink);

        const cartLink = document.createElement('a');
        cartLink.id = 'cart-link';
        cartLink.href = '/shop/index.html';   // ⬅️ ruta absoluta desde la raíz del sitio
        cartLink.textContent = '🛒 Carrito';
        menu.appendChild(cartLink);
    } else {
        const loginLink = document.createElement('a');
        loginLink.href = '/login/index.html';
        loginLink.textContent = 'Iniciar sesión';
        menu.appendChild(loginLink);

        const registerLink = document.createElement('a');
        registerLink.href = '/register/index.html';
        registerLink.textContent = 'Registrarse';
        menu.appendChild(registerLink);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    actualizarMenu();
});