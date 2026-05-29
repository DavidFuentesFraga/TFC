from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nombre

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    creado = models.DateTimeField(auto_now_add=True)

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrito', 'producto')

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    fecha = models.DateTimeField(auto_now_add=True)
    productos = models.ManyToManyField(
        Producto,
        through='DetallePedido',
        related_name='pedidos'
    )

    def __str__(self):
        return f"Pedido {self.id} - {self.fecha}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('pedido', 'producto')
