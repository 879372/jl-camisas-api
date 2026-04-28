from django.db import models
from core.models import TimestampMixin

class Cliente(TimestampMixin):
    TIPO_CHOICES = (
        ('fisica', 'Física'),
        ('juridica', 'Jurídica'),
    )
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='fisica')
    cpf_cnpj = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=150, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    logradouro = models.CharField(max_length=200, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome
