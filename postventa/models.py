from django.db import models

class Ticket(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COBRADO', 'Cobrado'),
        ('TERMINADO', 'Terminado'),
    ]
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    pedido_completado = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket #{self.id} - {self.estado}"

class ProductoTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='productos')
    codigo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    @property
    def total(self):
        return self.precio * self.cantidad

    def __str__(self):
        return f"{self.nombre} (x{self.cantidad}) - Ticket #{self.ticket.id}"
