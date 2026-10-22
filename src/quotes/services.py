import re
import uuid
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from src.customers.models import Customer
from src.orders.models import Order, OrderItem

from .models import QuoteConfig, QuoteOption


class QuoteService:
    REQUIRED_SELECTIONS = ('quantidade', 'prazo', 'modelo', 'estampa', 'tecido')

    @staticmethod
    def _clean_phone(value):
        phone = re.sub(r'\D', '', str(value or ''))
        if len(phone) not in (10, 11, 12, 13):
            raise ValidationError({'whatsapp': 'Informe um WhatsApp válido com DDD.'})
        if len(phone) <= 11:
            phone = f'55{phone}'
        return phone

    @classmethod
    def _calculate_amount(cls, data):
        config = QuoteConfig.objects.filter(is_active=True).order_by('id').first()
        total = config.base_amount if config else Decimal('0.00')

        for category in cls.REQUIRED_SELECTIONS:
            label = str(data.get(category) or '').strip()
            if not label:
                raise ValidationError({category: 'Selecione uma opção válida.'})
            option = QuoteOption.objects.filter(
                category=category, label=label, is_active=True
            ).first()
            if not option:
                raise ValidationError({category: 'A opção selecionada não está disponível.'})
            total += option.additional_amount

        additional_labels = data.get('adicionais') or []
        if not isinstance(additional_labels, list):
            raise ValidationError({'adicionais': 'Envie uma lista de adicionais.'})
        additional_options = QuoteOption.objects.filter(
            category='adicional', label__in=additional_labels, is_active=True
        )
        if additional_options.count() != len(set(additional_labels)):
            raise ValidationError({'adicionais': 'Um ou mais adicionais não estão disponíveis.'})

        return total + sum(
            (option.additional_amount for option in additional_options),
            Decimal('0.00'),
        )

    @classmethod
    @transaction.atomic
    def create_public_quote(cls, data):
        name = str(data.get('nome') or '').strip()
        if len(name) < 3:
            raise ValidationError({'nome': 'Informe o nome do cliente.'})

        phone = cls._clean_phone(data.get('whatsapp'))
        amount = cls._calculate_amount(data)

        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            if customer.name != name:
                customer.name = name
                customer.save(update_fields=['name', 'updated_at'])
        else:
            customer = Customer.objects.create(name=name, phone=phone, type='fisica')

        order_number = f'ORC-{uuid.uuid4().hex[:10].upper()}'
        order = Order.objects.create(
            number=order_number,
            customer=customer,
            status='orcamento',
        )

        specifications = {
            'quantidade': data.get('quantidade'),
            'modelo': data.get('modelo'),
            'estampa': data.get('estampa'),
            'tecido': data.get('tecido'),
            'adicionais': data.get('adicionais', []),
            'prazo': data.get('prazo'),
        }
        OrderItem.objects.create(
            order=order,
            description='Camisas Personalizadas - Orçamento Site',
            quantity=1,
            unit_price=amount,
            specifications=specifications,
        )
        order.refresh_from_db(fields=['total_amount'])
        return order.number
