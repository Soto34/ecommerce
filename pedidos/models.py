from django.db import models

from django.db import models

class Pedido(models.Model):
    # Datos del destinatario
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    rut = models.CharField(max_length=12)

    # Datos de ubicación
    direccion = models.CharField(max_length=255)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)

    # Especificaciones adicionales
    especificaciones = models.TextField(blank=True, null=True)

    # Método de pago
    METODOS_PAGO = [
        ('Transferencia', 'Transferencia'),
        ('Paypal', 'Paypal'),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)

    # Fecha del pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido de {self.nombre} {self.apellido} - {self.metodo_pago}"
