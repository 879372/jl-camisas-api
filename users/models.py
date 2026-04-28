from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimestampMixin

class User(AbstractUser, TimestampMixin):
    PERFIL_CHOICES = (
        ('admin', 'Administrador'),
        ('operacional', 'Operacional'),
        ('financeiro', 'Financeiro'),
        ('vendas', 'Vendas'),
    )
    nome = models.CharField(max_length=120)
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='operacional')

    def __str__(self):
        return self.username
