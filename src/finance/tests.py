from decimal import Decimal

from django.test import TestCase

from src.customers.models import Customer
from src.orders.models import Order, OrderItem

from .serializers import TransactionSerializer


class TransactionSerializerTests(TestCase):
    def setUp(self):
        customer = Customer.objects.create(name='Cliente Financeiro')
        self.order = Order.objects.create(number='PED-FIN', customer=customer)
        OrderItem.objects.create(
            order=self.order,
            description='Pedido',
            quantity=1,
            unit_price=Decimal('100.00'),
        )

    def test_accepts_portuguese_contract_and_updates_payment_status(self):
        serializer = TransactionSerializer(data={
            'pedido': self.order.pk,
            'tipo': 'entrada',
            'descricao': 'Entrada do pedido',
            'valor': '40.00',
            'forma_pagamento': 'pix',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.order.refresh_from_db()

        self.assertEqual(self.order.paid_amount, Decimal('40.00'))
        self.assertEqual(self.order.payment_status, 'parcial')

    def test_rejects_zero_or_negative_amount(self):
        serializer = TransactionSerializer(data={
            'tipo': 'entrada',
            'descricao': 'Valor inválido',
            'valor': '0.00',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('valor', serializer.errors)
