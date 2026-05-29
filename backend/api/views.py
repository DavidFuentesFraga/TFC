from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Producto, Carrito, ItemCarrito, Pedido, DetallePedido
from .serializers import (
    ProductoSerializer, CarritoSerializer, ItemCarritoSerializer, PedidoSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# --- Autenticación ---
@extend_schema(
    tags=['Autenticación'],
    summary='Registrar usuario',
    description='Crea un nuevo usuario y devuelve un token de autenticación.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
                'email': {'type': 'string'},
            },
            'required': ['username', 'password'],
        }
    },
    responses={
        201: {
            'type': 'object',
            'properties': {
                'token': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'username': {'type': 'string'},
            },
        },
    },
)

class RegistroView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        if not username or not password:
            return Response({'error': 'username y password requeridos'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'El usuario ya existe'}, status=400)
        user = User.objects.create_user(username=username, password=password, email=email)
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username}, status=201)

@extend_schema(
    tags=['Autenticación'],
    summary='Iniciar sesión',
    description='Valida credenciales y devuelve token de autenticación.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
            },
            'required': ['username', 'password'],
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'token': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'username': {'type': 'string'},
            },
        },
    },
)
class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username})

# --- Productos ---
@extend_schema(
    tags=['Productos'],
    summary='Listar productos',
    description='Devuelve todos los productos con stock disponible. Se puede filtrar por categoría.',
    parameters=[
        OpenApiParameter(
            name='categoria',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtra por categoría (tacos, bolas, mesas, accesorios, ropa).',
            required=False,
        ),
    ],
    responses={200: ProductoSerializer(many=True)},
)
class ProductoList(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categoria = request.query_params.get('categoria')
        productos = Producto.objects.filter(stock__gt=0)
        if categoria:
            productos = productos.filter(categoria__iexact=categoria)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

@extend_schema(
    tags=['Productos'],
    summary='Detalle de producto',
    description='Devuelve los datos de un producto específico.',
    responses={200: ProductoSerializer},
)
class ProductoDetail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)

# --- Carrito ---
@extend_schema(
    tags=['Carrito'],
    summary='Añadir producto al carrito',
    description='Añade una cantidad de un producto al carrito del usuario autenticado.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'producto_id': {'type': 'integer', 'description': 'ID del producto'},
                'cantidad': {'type': 'integer', 'description': 'Cantidad a añadir (por defecto 1)'},
            },
            'required': ['producto_id'],
        }
    },
    responses={201: ItemCarritoSerializer},
)
class AgregarAlCarrito(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))
        producto = get_object_or_404(Producto, pk=producto_id)

        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        if producto.stock < cantidad:
            return Response({'error': 'Stock insuficiente'}, status=400)

        item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()

        serializer = ItemCarritoSerializer(item)
        return Response(serializer.data, status=201)

@extend_schema(
    tags=['Carrito'],
    summary='Ver carrito',
    description='Devuelve el contenido actual del carrito del usuario autenticado.',
    responses={200: CarritoSerializer},
)
class VerCarrito(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

@extend_schema(
    tags=['Carrito'],
    summary='Modificar o eliminar ítem del carrito',
    description='PATCH para modificar la cantidad, DELETE para eliminar el ítem.',
    responses={
        200: ItemCarritoSerializer,
        204: None,
    },
)
class ItemCarritoUpdateDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        item = get_object_or_404(ItemCarrito, pk=pk, carrito__usuario=request.user)
        cantidad = request.data.get('cantidad')
        if cantidad is None:
            return Response({'error': 'cantidad requerida'}, status=400)
        if int(cantidad) <= 0:
            item.delete()
            return Response(status=204)
        if item.producto.stock < int(cantidad):
            return Response({'error': 'Stock insuficiente'}, status=400)
        item.cantidad = cantidad
        item.save()
        serializer = ItemCarritoSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        item = get_object_or_404(ItemCarrito, pk=pk, carrito__usuario=request.user)
        item.delete()
        return Response(status=204)

# --- Pedidos ---
@extend_schema(
    tags=['Pedidos'],
    summary='Finalizar compra',
    description='Crea un pedido con los productos del carrito, descuenta el stock y vacía el carrito.',
    responses={201: PedidoSerializer},
)
class FinalizarCompra(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        carrito = get_object_or_404(Carrito, usuario=request.user)
        items = carrito.items.all()
        if not items.exists():
            return Response({'error': 'Carrito vacío'}, status=400)

        pedido = Pedido.objects.create(usuario=request.user)
        for item in items:
            producto = item.producto
            if producto.stock < item.cantidad:
                pedido.delete()
                return Response({'error': f'Stock insuficiente para {producto.nombre}'}, status=400)
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item.cantidad,
                precio_unitario=producto.precio
            )
            producto.stock -= item.cantidad
            producto.save()

        items.delete()
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data, status=201)

@extend_schema(
    tags=['Pedidos'],
    summary='Historial de pedidos',
    description='Devuelve los pedidos realizados por el usuario autenticado.',
    responses={200: PedidoSerializer(many=True)},
)
class HistorialPedidos(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

@extend_schema(
    tags=['Autenticación'],
    summary='Cambiar contraseña',
    description='Permite al usuario autenticado cambiar su contraseña.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'old_password': {'type': 'string'},
                'new_password': {'type': 'string'},
            },
            'required': ['old_password', 'new_password'],
        }
    },
)

class CambiarPassword(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password and not new_password:
            return Response(
                {'error':'Se requieren old_password y new_password '},
                status=400
            )

        user = request.user
        if not user.check_password(old_password):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=400
            )

        user.set_password(new_password)
        user.save()
        return Response({'mensaje': 'Contraseña actualizada correctamente'})