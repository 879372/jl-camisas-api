from django.test import TestCase

from .serializers import CustomerSerializer


class CustomerSerializerTests(TestCase):
    def test_accepts_and_returns_portuguese_contract(self):
        serializer = CustomerSerializer(data={
            'nome': 'Cliente Teste',
            'tipo': 'fisica',
            'cpf_cnpj': '12345678901',
            'telefone': '84999999999',
            'uf': 'rn',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        customer = serializer.save()

        self.assertEqual(customer.name, 'Cliente Teste')
        self.assertEqual(customer.state, 'RN')
        self.assertEqual(CustomerSerializer(customer).data['nome'], 'Cliente Teste')

    def test_rejects_invalid_document_length(self):
        serializer = CustomerSerializer(data={
            'nome': 'Cliente Teste',
            'tipo': 'fisica',
            'cpf_cnpj': '123',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('cpf_cnpj', serializer.errors)
