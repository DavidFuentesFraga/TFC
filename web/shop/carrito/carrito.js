const API_BASE = 'http://127.0.0.1:8000/api';

// ---------- FUNCIONES DE AUTENTICACIÓN ----------
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

// ---------- FUNCIONES DEL CARRITO ----------
async function cargarCarrito() {
    if (!localStorage.getItem('auth_token')) {
        window.location.href = '/web/login/index.html';
        return;
    }

    const res = await fetch(`${API_BASE}/carrito/`, {
        headers: getAuthHeaders()
    });

    if (res.ok) {
        const data = await res.json();
        mostrarCarrito(data.items);
    } else if (res.status === 404) {
        mostrarCarrito([]); // carrito vacío
    } else {
        alert('Error al cargar el carrito');
    }
}

function mostrarCarrito(items) {
    const contenedor = document.getElementById('carrito-contenedor');
    let total = 0;

    if (!items || items.length === 0) {
        contenedor.innerHTML = '<p style="text-align:center; color:#aaa;">Tu carrito está vacío.</p>';
        document.getElementById('total').textContent = '0.00';
        return;
    }

    contenedor.innerHTML = items.map(item => {
        const subtotal = item.producto.precio * item.cantidad;
        total += subtotal;
        return `
            <div class="item-carrito" style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem; padding:1rem; background:#2a2a2a; border-radius:8px;">
                <img src="${item.producto.imagen ? 'http://127.0.0.1:8000' + item.producto.imagen : 'img/default.jpg'}" alt="${item.producto.nombre}" style="width:80px; height:80px; object-fit:cover; border-radius:6px;">
                <div style="flex:1;">
                    <h4 style="color:#fff;">${item.producto.nombre}</h4>
                    <p style="color:#00ff88;">${item.producto.precio} €</p>
                </div>
                <div>
                    <label style="color:#ccc; font-size:0.9rem;">Cantidad:</label>
                    <input type="number" value="${item.cantidad}" min="1" max="${item.producto.stock}" data-id="${item.id}" class="cantidad-input" style="width:60px; padding:5px; background:#1a1a1a; color:#fff; border:1px solid #555; border-radius:4px; margin-left:5px;">
                </div>
                <div>
                    <strong style="color:#00ff88;">${subtotal.toFixed(2)} €</strong>
                </div>
                <button class="btn-eliminar" data-id="${item.id}" style="background:none; border:none; color:#ff5555; font-size:1.5rem; cursor:pointer;">🗑️</button>
            </div>
        `;
    }).join('');

    document.getElementById('total').textContent = total.toFixed(2);

    // Eventos para cambiar cantidad (PATCH)
    document.querySelectorAll('.cantidad-input').forEach(input => {
        input.addEventListener('change', async (e) => {
            const itemId = e.target.dataset.id;
            const cantidad = parseInt(e.target.value);
            if (cantidad < 1) return;

            const res = await fetch(`${API_BASE}/carrito/item/${itemId}/`, {
                method: 'PATCH',
                headers: getAuthHeaders(),
                body: JSON.stringify({ cantidad })
            });

            if (res.ok) {
                cargarCarrito(); // Refrescar
            } else {
                const error = await res.json();
                alert(error.error || 'Error al actualizar cantidad');
            }
        });
    });

    // Eventos eliminar (DELETE)
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const itemId = e.target.dataset.id;
            const res = await fetch(`${API_BASE}/carrito/item/${itemId}/`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (res.ok) {
                cargarCarrito(); // Refrescar
            } else {
                alert('Error al eliminar el producto');
            }
        });
    });
}

// ---------- INICIALIZACIÓN ----------
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

    // Evento para finalizar compra
    document.getElementById('btn-comprar').addEventListener('click', async () => {
        if (!localStorage.getItem('auth_token')) {
            alert('Debes iniciar sesión');
            window.location.href = '/web/login/index.html';
            return;
        }

        const res = await fetch(`${API_BASE}/pedidos/crear/`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (res.ok) {
            const data = await res.json();
            alert(`¡Compra realizada con éxito! Pedido #${data.id}`);
            cargarCarrito(); // Ahora estará vacío
        } else {
            const error = await res.json();
            alert(error.error || 'Error al finalizar la compra');
        }
    });

    // Cargar el carrito al iniciar
    cargarCarrito();
});