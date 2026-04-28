from django.db import models
from pedidos.models import Pedido

class Lancamento(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    )
    FORMA_PAG_CHOICES = (
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('boleto', 'Boleto'),
        ('transferencia', 'Transferência'),
    )
    pedido = models.ForeignKey(Pedido, related_name='lancamentos', null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=300)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    forma_pagamento = models.CharField(max_length=30, choices=FORMA_PAG_CHOICES, null=True, blank=True)
    data_lancamento = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class NotaFiscal(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='notas_fiscais', null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=10) # nfe | nfce
    numero = models.CharField(max_length=20, null=True, blank=True)
    serie = models.CharField(max_length=5, null=True, blank=True)
    chave_acesso = models.CharField(max_length=44, unique=True, null=True, blank=True)
    status = models.CharField(max_length=30, default='pendente')
    xml = models.TextField(null=True, blank=True)
    protocolo = models.CharField(max_length=50, null=True, blank=True)
    motivo_rejeicao = models.TextField(null=True, blank=True)
    emitida_em = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
