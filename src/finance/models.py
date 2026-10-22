from django.db import models
from src.orders.models import Order

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('boleto', 'Boleto'),
        ('transferencia', 'Transferência'),
    )
    order = models.ForeignKey(Order, related_name='transactions', null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    observations = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Invoice(models.Model):
    TYPE_CHOICES = (
        ('nfe', 'NF-e'),
        ('nfce', 'NFC-e'),
    )
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('autorizada', 'Autorizada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    )
    order = models.ForeignKey(Order, related_name='invoices', null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    number = models.CharField(max_length=20, null=True, blank=True)
    series = models.CharField(max_length=5, null=True, blank=True)
    access_key = models.CharField(max_length=44, unique=True, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pendente')
    xml = models.TextField(null=True, blank=True)
    protocol = models.CharField(max_length=50, null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
