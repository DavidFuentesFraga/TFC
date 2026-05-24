const API_BASE = 'http://127.0.0.1:8000/api';

// ---------- AUTENTICACIÓN Y MENÚ ----------
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

// ---------- CATÁLOGO Y CARRITO ----------
async function cargarProductos(categoria = '') {
    const contenedor = document.getElementById('catalogo');
    if (!contenedor) return;

    let url = `${API_BASE}/productos/`;
    if (categoria) url += `?categoria=${categoria}`;
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('Error al obtener productos');
        const productos = await res.json();
        mostrarProductos(productos);
    } catch (error) {
        console.error(error);
        contenedor.innerHTML = '<p style="color:red;">Error al cargar productos</p>';
    }
}

function mostrarProductos(productos) {
    const contenedor = document.getElementById('catalogo');
    if (!contenedor) return;

    if (productos.length === 0) {
        contenedor.innerHTML = '<p style="text-align:center; color:#aaa;">No hay productos disponibles en esta categoría.</p>';
        return;
    }

    contenedor.innerHTML = productos.map(p => `
        <div class="producto">
            <img src="${p.imagen || 'img/default.jpg'}" alt="${p.nombre}">
            <h3>${p.nombre}</h3>
            <p class="precio">${p.precio} €</p>
            <p class="stock ${p.stock === 0 ? 'agotado' : ''}">
                ${p.stock > 0 ? `Stock: ${p.stock}` : 'Agotado'}
            </p>
            <button class="btn-agregar" data-id="${p.id}" ${p.stock === 0 ? 'disabled' : ''}>
                Añadir al carrito
            </button>
        </div>
    `).join('');

    document.querySelectorAll('.btn-agregar').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const productoId = e.target.dataset.id;
            await agregarAlCarrito(productoId, 1);
        });
    });
}

async function agregarAlCarrito(productoId, cantidad) {
    if (!localStorage.getItem('auth_token')) {
        alert('Debes iniciar sesión para comprar');
        window.location.href = '/web/login/index.html';
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/carrito/agregar/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ producto_id: productoId, cantidad })
        });

        if (res.ok) {
            alert('Producto añadido al carrito');
        } else {
            const error = await res.json();
            alert(error.error || 'Error al añadir al carrito');
        }
    } catch (error) {
        alert('Error de conexión');
    }
}

// ---------- INICIALIZACIÓN ----------
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

    // Catálogo
    if (document.getElementById('catalogo')) {
        cargarProductos();
        // Eventos del submenú
        document.querySelectorAll('.subnav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const categoria = e.target.dataset.categoria;
                cargarProductos(categoria);
            });
        });
    }
});