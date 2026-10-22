from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from src.customers.models import Customer

from .models import Order
from .serializers import OrderFileSerializer, OrderSerializer


class OrderSerializerTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Cliente Pedido')

    def test_creates_order_and_calculates_total_on_server(self):
        serializer = OrderSerializer(data={
            'numero': 'PED-001',
            'cliente': self.customer.pk,
            'status': 'orcamento',
            'valor_total': '9999.00',
            'itens': [{
                'descricao': 'Camiseta',
                'quantidade': '3.00',
                'valor_unitario': '25.50',
                'valor_total': '1.00',
            }],
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        order.refresh_from_db()

        self.assertEqual(order.total_amount, Decimal('76.50'))
        self.assertEqual(serializer.data['cliente_nome'], 'Cliente Pedido')
        self.assertEqual(serializer.data['valor_total'], '76.50')

    def test_nested_update_recalculates_total(self):
        order = Order.objects.create(number='PED-002', customer=self.customer)
        create_serializer = OrderSerializer(
            order,
            data={'itens': [{
                'descricao': 'Banner', 'quantidade': '2.00', 'valor_unitario': '30.00',
            }]},
            partial=True,
        )
        self.assertTrue(create_serializer.is_valid(), create_serializer.errors)
        create_serializer.save()

        update_serializer = OrderSerializer(
            order,
            data={'itens': [{
                'descricao': 'Banner', 'quantidade': '1.00', 'valor_unitario': '12.00',
            }]},
            partial=True,
        )
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        update_serializer.save()
        order.refresh_from_db()

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, Decimal('12.00'))

    def test_rejects_order_without_items(self):
        serializer = OrderSerializer(data={
            'numero': 'PED-003',
            'cliente': self.customer.pk,
            'itens': [],
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('itens', serializer.errors)

    def test_rejects_unsafe_artwork_file_extension(self):
        order = Order.objects.create(number='PED-ARQUIVO', customer=self.customer)
        serializer = OrderFileSerializer(data={
            'pedido': order.pk,
            'nome_original': 'arquivo.exe',
            'caminho': SimpleUploadedFile('arquivo.exe', b'conteudo'),
            'mime_type': 'application/octet-stream',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('caminho', serializer.errors)
