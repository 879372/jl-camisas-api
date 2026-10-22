from rest_framework import serializers
from decimal import Decimal
from .models import Transaction, Invoice
from src.orders.models import Order

class TransactionSerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(
        source='order', queryset=Order.objects.all(), allow_null=True, required=False
    )
    tipo = serializers.ChoiceField(source='type', choices=Transaction.TYPE_CHOICES)
    descricao = serializers.CharField(source='description')
    valor = serializers.DecimalField(source='amount', max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    forma_pagamento = serializers.ChoiceField(
        source='payment_method', choices=Transaction.PAYMENT_METHOD_CHOICES,
        allow_blank=True, allow_null=True, required=False,
    )
    data_lancamento = serializers.DateTimeField(source='transaction_date', read_only=True)
    observacoes = serializers.CharField(source='observations', allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Transaction
        fields = [
            'id', 'pedido', 'tipo', 'descricao', 'valor', 'forma_pagamento',
            'data_lancamento', 'observacoes', 'created_at',
        ]
        read_only_fields = ['id', 'data_lancamento', 'created_at']

class InvoiceSerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(
        source='order', queryset=Order.objects.all(), allow_null=True, required=False
    )
    tipo = serializers.ChoiceField(source='type', choices=Invoice.TYPE_CHOICES)
    numero = serializers.CharField(source='number', allow_blank=True, allow_null=True, required=False)
    serie = serializers.CharField(source='series', allow_blank=True, allow_null=True, required=False)
    chave_acesso = serializers.CharField(source='access_key', allow_blank=True, allow_null=True, required=False)
    protocolo = serializers.CharField(source='protocol', allow_blank=True, allow_null=True, required=False)
    motivo_rejeicao = serializers.CharField(source='rejection_reason', allow_blank=True, allow_null=True, required=False)
    emitida_em = serializers.DateTimeField(source='issued_at', allow_null=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'id', 'pedido', 'tipo', 'numero', 'serie', 'chave_acesso', 'status',
            'xml', 'protocolo', 'motivo_rejeicao', 'emitida_em', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        order = attrs.get('order') or getattr(self.instance, 'order', None)
        invoice_type = attrs.get('type') or getattr(self.instance, 'type', None)
        if not order:
            raise serializers.ValidationError({'pedido': 'Vincule a nota fiscal a um pedido.'})
        if not order.items.exists():
            raise serializers.ValidationError({'pedido': 'O pedido não possui itens para faturamento.'})

        missing_items = []
        for item in order.items.select_related('product'):
            if not item.product or not item.product.ncm or not item.product.cfop:
                missing_items.append(item.description)
        if missing_items:
            raise serializers.ValidationError({
                'pedido': 'Complete produto, NCM e CFOP dos itens: ' + ', '.join(missing_items)
            })

        if invoice_type == 'nfe':
            customer = order.customer
            required_customer_data = {
                'CPF/CNPJ': customer.document_number,
                'logradouro': customer.street,
                'cidade': customer.city,
                'UF': customer.state,
                'CEP': customer.postal_code,
            }
            missing = [label for label, value in required_customer_data.items() if not value]
            if missing:
                raise serializers.ValidationError({
                    'pedido': 'Complete os dados fiscais do cliente: ' + ', '.join(missing)
                })

        duplicate = Invoice.objects.filter(
            order=order,
            type=invoice_type,
            status__in=('pendente', 'autorizada'),
        )
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError({'pedido': 'Já existe uma nota ativa deste tipo para o pedido.'})
        return attrs
