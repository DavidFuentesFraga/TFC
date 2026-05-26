const API_BASE = 'http://127.0.0.1:8000/api';

function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Token ${token}`;
    return headers;
}

function actualizarMenu() {
    const token = localStorage.getItem('auth_token');
    const linkLogin = document.getElementById('link-login');
    const linkRegister = document.getElementById('link-register');
    const userMenu = document.getElementById('user-menu');
    const userNameSpan = document.getElementById('user-name');
    const cartLink = document.getElementById('cart-link');

    if (!linkLogin || !linkRegister || !userMenu || !cartLink) return;

    if (token) {
        linkLogin.style.display = 'none';
        linkRegister.style.display = 'none';
        userMenu.style.display = 'inline';
        const username = localStorage.getItem('username');
        if (userNameSpan) userNameSpan.textContent = username || 'Usuario';
        cartLink.style.display = 'inline';
    } else {
        linkLogin.style.display = 'inline';
        linkRegister.style.display = 'inline';
        userMenu.style.display = 'none';
        cartLink.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    actualizarMenu();

    // Dropdown del usuario
    const userNameLink = document.getElementById('user-name-link');
    const userDropdown = document.getElementById('user-dropdown');
    if (userNameLink && userDropdown) {
        userNameLink.addEventListener('click', (e) => {
            e.preventDefault();
            userDropdown.style.display = userDropdown.style.display === 'none' ? 'block' : 'none';
        });
    }

    // Cerrar sesión
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('auth_token');
            localStorage.removeItem('username');
            window.location.reload();
        });
    }
});
