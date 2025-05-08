from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    codigo = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    stock = models.IntegerField()
    stock_min = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/',null=True, blank=True)

    def __str__(self):
        return self.name