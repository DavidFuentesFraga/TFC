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

    // Dropdown y logout
    const userNameLink = document.getElementById('user-name-link');
    const userDropdown = document.getElementById('user-dropdown');
    if (userNameLink && userDropdown) {
        userNameLink.addEventListener('click', (e) => {
            e.preventDefault();
            userDropdown.style.display = userDropdown.style.display === 'none' ? 'block' : 'none';
        });
    }
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('auth_token');
            localStorage.removeItem('username');
            window.location.reload();
        });
    }

    // Lógica del formulario de registro
    const form = document.getElementById('register-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const password2 = document.getElementById('password2').value;

            if (password !== password2) {
                alert('Las contraseñas no coinciden');
                return;
            }

            const res = await fetch(`${API_BASE}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, email })
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('username', data.username);
                window.location.href = '/web/shop/index.html';
            } else {
                const error = await res.json().catch(() => ({}));
                alert('Error al registrarse: ' + (error.error || 'Datos inválidos'));
            }
        });
    }
});