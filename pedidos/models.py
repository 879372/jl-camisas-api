from django.db import models
from core.models import TimestampMixin
from clientes.models import Cliente
from produtos.models import Produto
from django.conf import settings
from django.db.models import Sum

class Pedido(TimestampMixin):
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
    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, related_name='pedidos', on_delete=models.PROTECT)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='orcamento')
    status_pagamento = models.CharField(max_length=30, choices=STATUS_PAG_CHOICES, default='pendente')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_pago = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    data_entrega_prevista = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    observacoes_internas = models.TextField(null=True, blank=True)

    def recalculate_total(self):
        total = self.itens.aggregate(total=Sum('valor_total'))['total'] or 0
        self.valor_total = total
        self.save()

    def __str__(self):
        return self.numero

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, null=True, blank=True, on_delete=models.SET_NULL)
    descricao = models.CharField(max_length=300)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    especificacoes = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.valor_total = (self.quantidade or 0) * (self.valor_unitario or 0)
        super().save(*args, **kwargs)
        # Recalculate parent order total
        if self.pedido:
            # We use a signal-like approach or just call the method
            # To avoid recursion if recalculate_total calls save()
            total = self.pedido.itens.aggregate(total=Sum('valor_total'))['total'] or 0
            Pedido.objects.filter(id=self.pedido.id).update(valor_total=total)

class PedidoArquivo(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='arquivos', on_delete=models.CASCADE)
    nome_original = models.CharField(max_length=300)
    caminho = models.FileField(upload_to='pedidos_arquivos/')
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    tamanho_bytes = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PedidoHistorico(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='historico', on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    acao = models.CharField(max_length=300)
    detalhe = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
