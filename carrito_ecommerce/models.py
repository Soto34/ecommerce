from django.db import models
from decimal import Decimal
from django.conf import settings  

class TicketEcommerce(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tickets'
    )
    email_usuario = models.EmailField(null=True, blank=True)  # <--- Agregado

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    comuna = models.CharField(max_length=100)

    metodo_pago = models.CharField(
        max_length=20,
        choices=[('paypal', 'PayPal'), ('transferencia', 'Transferencia')],
        default='paypal'
    )

    estado_pago = models.CharField(max_length=20, choices=[
        ('pagado', 'Pagado'),
        ('pendiente', 'Pendiente')
    ], default='pendiente')

    estado_envio = models.CharField(max_length=30, choices=[
        ('recolectando productos', 'Recolectando productos'),
        ('productos recolectados', 'Productos recolectados'),
        ('producto entregado', 'Producto entregado')
    ], default='recolectando productos')

    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        total = sum(item.precio * item.cantidad for item in self.productos.all())
        if self.productos.count() >= 4:
            total -= total * Decimal('0.05')
        return total
    
class ProductoTicketEcommerce(models.Model):
    ticket = models.ForeignKey(TicketEcommerce, related_name='productos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    def subtotal(self):
        return self.precio * self.cantidad
