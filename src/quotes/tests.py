from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from src.orders.models import Order

from .models import QuoteConfig, QuoteOption
from .services import QuoteService


class QuoteServiceTests(TestCase):
    def setUp(self):
        QuoteConfig.objects.all().delete()
        QuoteConfig.objects.create(base_amount=Decimal('50.00'))
        for category in QuoteService.REQUIRED_SELECTIONS:
            QuoteOption.objects.create(
                category=category,
                label=f'Opção {category}',
                additional_amount=Decimal('2.00'),
            )
        QuoteOption.objects.create(
            category='adicional',
            label='Embalagem',
            additional_amount=Decimal('5.00'),
        )

    def test_calculates_price_on_server_and_ignores_browser_total(self):
        payload = {
            'nome': 'Cliente Orçamento',
            'whatsapp': '(84) 99999-9999',
            'valor_total': '0.01',
            'adicionais': ['Embalagem'],
        }
        for category in QuoteService.REQUIRED_SELECTIONS:
            payload[category] = f'Opção {category}'

        number = QuoteService.create_public_quote(payload)
        order = Order.objects.get(number=number)

        self.assertEqual(order.total_amount, Decimal('65.00'))
        self.assertTrue(number.startswith('ORC-'))

    def test_rejects_unknown_option(self):
        payload = {
            'nome': 'Cliente Orçamento',
            'whatsapp': '84999999999',
            'adicionais': [],
        }
        for category in QuoteService.REQUIRED_SELECTIONS:
            payload[category] = f'Opção {category}'
        payload['tecido'] = 'Opção inexistente'

        with self.assertRaises(ValidationError):
            QuoteService.create_public_quote(payload)


class QuoteConfigApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='quote-admin',
            password='senha-segura-123',
            name='Administrador',
            profile='admin',
        )
        self.client.force_authenticate(user)

    def test_seeded_config_prevents_duplicate_general_configuration(self):
        list_response = self.client.get('/api/v1/orcamento-publico/config/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

        create_response = self.client.post('/api/v1/orcamento-publico/config/', {
            'whatsapp_destino': '5584999999999',
            'mensagem_template': 'Olá, {nome}',
            'valor_base': '10.00',
            'ativo': True,
        }, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)
