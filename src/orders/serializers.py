from decimal import Decimal
from pathlib import Path

from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers

from src.customers.models import Customer
from src.products.models import Product

from .models import Order, OrderFile, OrderHistory, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(
        source='order', queryset=Order.objects.all(), required=False
    )
    produto = serializers.PrimaryKeyRelatedField(
        source='product', queryset=Product.objects.all(), allow_null=True, required=False
    )
    descricao = serializers.CharField(source='description')
    quantidade = serializers.DecimalField(
        source='quantity', max_digits=10, decimal_places=2, min_value=Decimal('0.01')
    )
    valor_unitario = serializers.DecimalField(
        source='unit_price', max_digits=12, decimal_places=2, min_value=Decimal('0.00')
    )
    valor_total = serializers.DecimalField(
        source='total_price', max_digits=12, decimal_places=2, read_only=True
    )
    especificacoes = serializers.JSONField(source='specifications', allow_null=True, required=False)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'pedido', 'produto', 'descricao', 'quantidade',
            'valor_unitario', 'valor_total', 'especificacoes',
        ]
        read_only_fields = ['id', 'valor_total']


class OrderFileSerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(source='order', queryset=Order.objects.all())
    nome_original = serializers.CharField(source='original_name')
    caminho = serializers.FileField(source='file_path')
    tamanho_bytes = serializers.IntegerField(source='size_bytes', min_value=0, required=False, allow_null=True)

    class Meta:
        model = OrderFile
        fields = [
            'id', 'pedido', 'nome_original', 'caminho', 'mime_type',
            'tamanho_bytes', 'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at']

    def validate_caminho(self, value):
        if value.size > 25 * 1024 * 1024:
            raise serializers.ValidationError('O arquivo deve ter no máximo 25 MB.')
        allowed_extensions = {
            '.ai', '.cdr', '.eps', '.jpeg', '.jpg', '.pdf', '.png', '.psd',
            '.rar', '.svg', '.tif', '.tiff', '.zip',
        }
        extension = Path(value.name).suffix.lower()
        if extension not in allowed_extensions:
            allowed = ', '.join(sorted(allowed_extensions))
            raise serializers.ValidationError(
                f'Formato não permitido. Extensões aceitas: {allowed}.'
            )
        return value


class OrderHistorySerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(source='order', read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    acao = serializers.CharField(source='action', read_only=True)
    detalhe = serializers.CharField(source='detail', read_only=True)

    class Meta:
        model = OrderHistory
        fields = ['id', 'pedido', 'usuario', 'acao', 'detalhe', 'created_at']
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    numero = serializers.CharField(source='number')
    cliente = serializers.PrimaryKeyRelatedField(source='customer', queryset=Customer.objects.all())
    cliente_nome = serializers.CharField(source='customer.name', read_only=True)
    status_pagamento = serializers.CharField(source='payment_status', read_only=True)
    valor_total = serializers.DecimalField(
        source='total_amount', max_digits=12, decimal_places=2, read_only=True
    )
    valor_pago = serializers.DecimalField(
        source='paid_amount', max_digits=12, decimal_places=2, read_only=True
    )
    data_entrega_prevista = serializers.DateField(
        source='expected_delivery_date', allow_null=True, required=False
    )
    observacoes = serializers.CharField(source='observations', allow_blank=True, allow_null=True, required=False)
    observacoes_internas = serializers.CharField(
        source='internal_observations', allow_blank=True, allow_null=True, required=False
    )
    transportadora = serializers.CharField(source='carrier', allow_blank=True, allow_null=True, required=False)
    codigo_rastreio = serializers.CharField(source='tracking_code', allow_blank=True, allow_null=True, required=False)
    enviado_em = serializers.DateTimeField(source='shipped_at', allow_null=True, required=False)
    entregue_em = serializers.DateTimeField(source='delivered_at', allow_null=True, required=False)
    itens = OrderItemSerializer(source='items', many=True, required=False)
    arquivos = OrderFileSerializer(source='files', many=True, read_only=True)
    historico = OrderHistorySerializer(source='history', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'numero', 'cliente', 'cliente_nome', 'status',
            'status_pagamento', 'valor_total', 'valor_pago',
            'data_entrega_prevista', 'observacoes', 'observacoes_internas',
            'transportadora', 'codigo_rastreio', 'enviado_em', 'entregue_em',
            'itens', 'arquivos', 'historico', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status_pagamento', 'valor_total', 'valor_pago',
            'arquivos', 'historico', 'created_at', 'updated_at',
        ]

    def validate_itens(self, value):
        if not value:
            raise serializers.ValidationError('O pedido deve possuir pelo menos um item.')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get('delivered_at'):
            attrs['status'] = 'concluido'
        return attrs

    @staticmethod
    def _update_total(order):
        total = order.items.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
        Order.objects.filter(pk=order.pk).update(total_amount=total)
        order.total_amount = total

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        if not items_data:
            raise serializers.ValidationError({'itens': 'O pedido deve possuir pelo menos um item.'})

        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            item_data.pop('order', None)
            OrderItem.objects.create(order=order, **item_data)
        self._update_total(order)
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            if not items_data:
                raise serializers.ValidationError({'itens': 'O pedido deve possuir pelo menos um item.'})
            instance.items.all().delete()
            for item_data in items_data:
                item_data.pop('order', None)
                OrderItem.objects.create(order=instance, **item_data)
            self._update_total(instance)

        return instance
