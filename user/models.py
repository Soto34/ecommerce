from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, nombre=None, apellido=None, rut=None, rol='cliente', **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, apellido=apellido, rut=rut, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, nombre=None, apellido=None, rut=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        rol = 'admin'
        user = self.create_user(email, password, nombre, apellido, rut, rol, **extra_fields)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('cliente', 'Cliente'),
        ('contador', 'Contador'),
        ('bodeguero', 'Bodeguero'),
        ('repartidor', 'Repartidor'),
        ('cajero', 'Cajero'), 
        ('admin', 'Administrador'),
    )

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    rut = models.CharField(max_length=12, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Evita conflicto related_name (ajusta según tu estructura de apps)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        verbose_name='grupos',
        help_text='Los grupos a los que pertenece este usuario.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True,
        verbose_name='permisos de usuario',
        help_text='Permisos específicos para este usuario.',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'rut']

    def __str__(self):
        return f'{self.email} ({self.rol})'