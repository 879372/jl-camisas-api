from django.db import models
from django.contrib.auth.models import AbstractUser
from src.core.models import TimestampMixin

class User(AbstractUser, TimestampMixin):
    REQUIRED_FIELDS = ['name']
    PROFILE_CHOICES = (
        ('admin', 'Administrador'),
        ('operacional', 'Operacional'),
        ('financeiro', 'Financeiro'),
        ('vendas', 'Vendas'),
    )
    name = models.CharField(max_length=120)
    profile = models.CharField(max_length=20, choices=PROFILE_CHOICES, default='operacional')

    def __str__(self):
        return self.username
