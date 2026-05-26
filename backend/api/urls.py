from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('register/', views.RegistroView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('cambiar-password/', views.CambiarPassword.as_view(), name='cambiar-password'),

    # Productos
    path('productos/', views.ProductoList.as_view(), name='producto-list'),
    path('productos/<int:pk>/', views.ProductoDetail.as_view(), name='producto-detail'),

    # Carrito
    path('carrito/agregar/', views.AgregarAlCarrito.as_view(), name='carrito-agregar'),
    path('carrito/', views.VerCarrito.as_view(), name='ver-carrito'),
    path('carrito/item/<int:pk>/', views.ItemCarritoUpdateDelete.as_view(), name='item-carrito-update-delete'),

    # Pedidos
    path('pedidos/crear/', views.FinalizarCompra.as_view(), name='pedido-crear'),
    path('pedidos/', views.HistorialPedidos.as_view(), name='historial-pedidos'),
]