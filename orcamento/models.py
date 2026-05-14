from django.db import models
from core.models import TimestampMixin

class OrcamentoConfig(models.Model):
    whatsapp_destino = models.CharField(max_length=20, default='5584994274111')
    mensagem_template = models.TextField(default="Olá, meu nome é {nome} e realizei um orçamento pelo site.")
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return "Configuração Geral do Orçamento"

    class Meta:
        verbose_name = "Configuração Geral"
        verbose_name_plural = "Configurações Gerais"

class OrcamentoOpcao(models.Model):
    CATEGORIA_CHOICES = (
        ('quantidade', 'Quantidade'),
        ('prazo', 'Prazo'),
        ('modelo', 'Modelo'),
        ('estampa', 'Estampa'),
        ('tecido', 'Tecido'),
        ('adicional', 'Adicional'),
    )
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    label = models.CharField(max_length=100)
    valor_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descricao = models.TextField(null=True, blank=True)
    icone = models.CharField(max_length=50, null=True, blank=True, help_text="Emoji ou nome do ícone")
    ordem = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.label}"

    class Meta:
        verbose_name = "Opção de Orçamento"
        verbose_name_plural = "Opções de Orçamento"
        ordering = ['categoria', 'ordem', 'label']
