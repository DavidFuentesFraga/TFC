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

# --- Autenticación ---
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

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username})

# --- Productos ---
class ProductoList(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categoria = request.query_params.get('categoria')
        productos = Producto.objects.filter(stock__gt=0)
        if categoria:
            productos = productos.filter(categoria__iexact=categoria)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

class ProductoDetail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)

# --- Carrito ---
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

class VerCarrito(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

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

class HistorialPedidos(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

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