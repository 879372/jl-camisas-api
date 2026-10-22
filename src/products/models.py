from django.db import models
from src.core.models import TimestampMixin

class Product(TimestampMixin):
    ORIGIN_CHOICES = (
        ('0', 'Nacional'),
        ('1', 'Estrangeira - importação direta'),
        ('2', 'Estrangeira - adquirida no mercado interno'),
        ('3', 'Nacional com conteúdo importado superior a 40%'),
        ('5', 'Nacional com conteúdo importado inferior ou igual a 40%'),
        ('8', 'Nacional com conteúdo importado superior a 70%'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, default='un')
    is_active = models.BooleanField(default=True)
    ncm = models.CharField(max_length=8, null=True, blank=True)
    cest = models.CharField(max_length=7, null=True, blank=True)
    cfop = models.CharField(max_length=4, null=True, blank=True)
    origin = models.CharField(max_length=1, choices=ORIGIN_CHOICES, default='0')
    icms_code = models.CharField(max_length=3, null=True, blank=True)
    csosn = models.CharField(max_length=3, null=True, blank=True)
    icms_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ipi_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pis_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cofins_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"
