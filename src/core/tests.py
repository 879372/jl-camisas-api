from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from src.finance.models import Invoice


class CoreCrudApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='tester',
            password='senha-segura-123',
            name='Usuário de Teste',
            profile='admin',
        )
        self.client.force_authenticate(user)

    def test_customer_create_list_update_delete_and_pagination(self):
        create_response = self.client.post('/api/v1/customers/', {
            'nome': 'Cliente API',
            'tipo': 'fisica',
            'cpf_cnpj': '12345678901',
        }, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        customer_id = create_response.data['id']

        update_response = self.client.patch(
            f'/api/v1/customers/{customer_id}/',
            {'nome': 'Cliente Atualizado'},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['nome'], 'Cliente Atualizado')

        for index in range(50):
            self.client.post('/api/v1/customers/', {
                'nome': f'Cliente {index}',
                'tipo': 'fisica',
            }, format='json')

        list_response = self.client.get('/api/v1/customers/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 51)
        self.assertEqual(len(list_response.data['results']), 50)
        self.assertIsNotNone(list_response.data['next'])

        delete_response = self.client.delete(f'/api/v1/customers/{customer_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_order_transaction_and_invoice_routes_use_frontend_contract(self):
        customer = self.client.post('/api/v1/customers/', {
            'nome': 'Cliente Fluxo',
            'tipo': 'fisica',
            'cpf_cnpj': '12345678901',
            'logradouro': 'Rua de Teste',
            'cidade': 'Natal',
            'uf': 'RN',
            'cep': '59000000',
        }, format='json').data
        product_response = self.client.post('/api/v1/products/', {
            'nome': 'Camiseta',
            'descricao': 'Camiseta personalizada',
            'preco_base': '30.00',
            'unidade': 'un',
            'ativo': True,
            'ncm': '61091000',
            'cfop': '5102',
        }, format='json')
        self.assertEqual(product_response.status_code, status.HTTP_201_CREATED)

        order_response = self.client.post('/api/v1/orders/', {
            'numero': 'PED-API-1',
            'cliente': customer['id'],
            'status': 'orcamento',
            'itens': [{
                'produto': product_response.data['id'],
                'descricao': 'Camiseta personalizada',
                'quantidade': '2.00',
                'valor_unitario': '30.00',
            }],
        }, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order_response.data['valor_total'], '60.00')

        transaction_response = self.client.post('/api/v1/transactions/', {
            'pedido': order_response.data['id'],
            'tipo': 'entrada',
            'descricao': 'Pagamento integral',
            'valor': '60.00',
            'forma_pagamento': 'pix',
        }, format='json')
        self.assertEqual(transaction_response.status_code, status.HTTP_201_CREATED)

        refreshed_order = self.client.get(
            f"/api/v1/orders/{order_response.data['id']}/"
        )
        self.assertEqual(refreshed_order.data['status_pagamento'], 'pago')

        invoice_response = self.client.post(
            f"/api/v1/orders/{order_response.data['id']}/concluir/",
            {'nota_fiscal': 'nfe'},
            format='json',
        )
        self.assertEqual(invoice_response.status_code, status.HTTP_200_OK)
        self.assertEqual(invoice_response.data['status'], 'concluido')

        invoice_list = self.client.get('/api/v1/notas-fiscais/')
        self.assertEqual(invoice_list.status_code, status.HTTP_200_OK)
        self.assertEqual(invoice_list.data['count'], 1)
        self.assertEqual(invoice_list.data['results'][0]['tipo'], 'nfe')

        invoice = Invoice.objects.get()
        invoice.xml = '<nfe><infNFe /></nfe>'
        invoice.access_key = '1' * 44
        invoice.save(update_fields=['xml', 'access_key'])
        export_response = self.client.get('/api/v1/notas-fiscais/exportar-xml/')
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        self.assertEqual(export_response['Content-Type'], 'application/zip')
        self.assertGreater(len(export_response.content), 0)

    def test_invoice_request_is_atomic_when_fiscal_data_is_missing(self):
        customer = self.client.post('/api/v1/customers/', {
            'nome': 'Cliente sem cadastro fiscal', 'tipo': 'fisica',
        }, format='json')
        product = self.client.post('/api/v1/products/', {
            'nome': 'Produto sem NCM', 'preco_base': '10.00',
            'unidade': 'un', 'ativo': True,
        }, format='json')
        order = self.client.post('/api/v1/orders/', {
            'numero': 'PED-SEM-FISCAL',
            'cliente': customer.data['id'],
            'itens': [{
                'produto': product.data['id'],
                'descricao': 'Produto sem NCM',
                'quantidade': '1.00',
                'valor_unitario': '10.00',
            }],
        }, format='json')

        response = self.client.post(
            f"/api/v1/orders/{order.data['id']}/concluir/",
            {'nota_fiscal': 'nfe'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order_after = self.client.get(f"/api/v1/orders/{order.data['id']}/")
        self.assertEqual(order_after.data['status'], 'orcamento')
