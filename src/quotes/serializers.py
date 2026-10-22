from rest_framework import serializers
from decimal import Decimal
from .models import QuoteConfig, QuoteOption

class QuoteConfigSerializer(serializers.ModelSerializer):
    whatsapp_destino = serializers.CharField(source='whatsapp_destination')
    mensagem_template = serializers.CharField(source='message_template')
    valor_base = serializers.DecimalField(
        source='base_amount', max_digits=10, decimal_places=2, min_value=Decimal('0.00')
    )
    ativo = serializers.BooleanField(source='is_active')

    class Meta:
        model = QuoteConfig
        fields = ['id', 'whatsapp_destino', 'mensagem_template', 'valor_base', 'ativo']
        read_only_fields = ['id']

class QuoteOptionSerializer(serializers.ModelSerializer):
    categoria = serializers.ChoiceField(source='category', choices=QuoteOption.CATEGORY_CHOICES)
    valor_adicional = serializers.DecimalField(
        source='additional_amount', max_digits=10, decimal_places=2, min_value=Decimal('0.00')
    )
    descricao = serializers.CharField(source='description', allow_blank=True, allow_null=True, required=False)
    icone = serializers.CharField(source='icon', allow_blank=True, allow_null=True, required=False)
    ordem = serializers.IntegerField(source='order_index', min_value=0)
    ativo = serializers.BooleanField(source='is_active')

    class Meta:
        model = QuoteOption
        fields = [
            'id', 'categoria', 'label', 'valor_adicional', 'descricao',
            'icone', 'ordem', 'ativo',
        ]
        read_only_fields = ['id']
