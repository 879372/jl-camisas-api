from django.db import models
from src.core.models import TimestampMixin
from src.customers.models import Customer
from src.products.models import Product
from django.conf import settings
from django.db.models import Sum

class Order(TimestampMixin):
    STATUS_CHOICES = (
        ('orcamento', 'Orçamento'),
        ('aguardando_pagamento', 'Aguardando Pagamento'),
        ('em_producao', 'Em Produção'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    )
    STATUS_PAG_CHOICES = (
        ('pendente', 'Pendente'),
        ('parcial', 'Parcial'),
        ('pago', 'Pago'),
    )
    number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='orcamento')
    payment_status = models.CharField(max_length=30, choices=STATUS_PAG_CHOICES, default='pendente')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_delivery_date = models.DateField(null=True, blank=True)
    observations = models.TextField(null=True, blank=True)
    internal_observations = models.TextField(null=True, blank=True)
    carrier = models.CharField(max_length=200, null=True, blank=True)
    tracking_code = models.CharField(max_length=100, null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def recalculate_total(self):
        total = self.items.aggregate(total=Sum('total_price'))['total'] or 0
        self.total_amount = total
        self.save()

    def __str__(self):
        return self.number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    specifications = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = (self.quantity or 0) * (self.unit_price or 0)
        super().save(*args, **kwargs)
        if self.order:
            total = self.order.items.aggregate(total=Sum('total_price'))['total'] or 0
            Order.objects.filter(id=self.order.id).update(total_amount=total)

    def delete(self, *args, **kwargs):
        order_id = self.order_id
        result = super().delete(*args, **kwargs)
        if order_id:
            total = OrderItem.objects.filter(order_id=order_id).aggregate(
                total=Sum('total_price')
            )['total'] or 0
            Order.objects.filter(id=order_id).update(total_amount=total)
        return result

class OrderFile(models.Model):
    order = models.ForeignKey(Order, related_name='files', on_delete=models.CASCADE)
    original_name = models.CharField(max_length=300)
    file_path = models.FileField(upload_to='orders_files/')
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    size_bytes = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class OrderHistory(models.Model):
    order = models.ForeignKey(Order, related_name='history', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=300)
    detail = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
