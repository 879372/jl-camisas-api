from django.db import models
from src.core.models import TimestampMixin

class QuoteConfig(models.Model):
    whatsapp_destination = models.CharField(max_length=20, default='5584994274111')
    message_template = models.TextField(default="Olá, meu nome é {nome} e realizei um orçamento pelo site.")
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Configuração Geral do Orçamento"

    class Meta:
        verbose_name = "Configuração Geral"
        verbose_name_plural = "Configurações Gerais"

class QuoteOption(models.Model):
    CATEGORY_CHOICES = (
        ('quantidade', 'Quantidade'),
        ('prazo', 'Prazo'),
        ('modelo', 'Modelo'),
        ('estampa', 'Estampa'),
        ('tecido', 'Tecido'),
        ('adicional', 'Adicional'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    label = models.CharField(max_length=100)
    additional_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True, help_text="Emoji ou nome do ícone")
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.label}"

    class Meta:
        verbose_name = "Opção de Orçamento"
        verbose_name_plural = "Opções de Orçamento"
        ordering = ['category', 'order_index', 'label']
