from django.db import models
from core.models import TimestampMixin

class Produto(TimestampMixin):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)
    preco_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidade = models.CharField(max_length=20, default='un')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class ProdutoVariacao(models.Model):
    produto = models.ForeignKey(Produto, related_name='variacoes', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    valor_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.produto.nome} - {self.nome}"
