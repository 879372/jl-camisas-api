from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from .models import User


class PermissionAndUserApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin-test', password='senha-forte-123',
            name='Admin', profile='admin',
        )
        self.sales = User.objects.create_user(
            username='sales-test', password='senha-forte-123',
            name='Vendas', profile='vendas',
        )
        self.operational = User.objects.create_user(
            username='ops-test', password='senha-forte-123',
            name='Operacional', profile='operacional',
        )
        self.client = APIClient()

    def test_me_returns_authenticated_user(self):
        self.client.force_authenticate(self.sales)
        response = self.client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile'], 'vendas')

    def test_sales_can_create_customer_but_cannot_delete(self):
        self.client.force_authenticate(self.sales)
        create_response = self.client.post('/api/v1/customers/', {
            'nome': 'Cliente Vendas', 'tipo': 'fisica',
        }, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        delete_response = self.client.delete(
            f"/api/v1/customers/{create_response.data['id']}/"
        )
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_operational_cannot_create_product(self):
        self.client.force_authenticate(self.operational)
        response = self.client.post('/api/v1/products/', {
            'nome': 'Produto Bloqueado',
            'preco_base': '10.00',
            'unidade': 'un',
            'ativo': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_admin_manages_users_and_password_is_hashed(self):
        self.client.force_authenticate(self.sales)
        self.assertEqual(
            self.client.get('/api/v1/users/').status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/v1/users/', {
            'username': 'novo-usuario',
            'name': 'Novo Usuário',
            'email': 'novo@example.com',
            'profile': 'financeiro',
            'is_active': True,
            'password': 'senha-nova-123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(username='novo-usuario')
        self.assertTrue(created.check_password('senha-nova-123'))
