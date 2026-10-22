from django.db import models
from src.core.models import TimestampMixin

class Customer(TimestampMixin):
    TYPE_CHOICES = (
        ('fisica', 'Física'),
        ('juridica', 'Jurídica'),
    )
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='fisica')
    document_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    number = models.CharField(max_length=10, null=True, blank=True)
    complement = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    observations = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
