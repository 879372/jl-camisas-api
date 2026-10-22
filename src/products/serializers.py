from rest_framework import serializers
from decimal import Decimal
from .models import Product, ProductVariation

class ProductVariationSerializer(serializers.ModelSerializer):
    produto = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all())
    nome = serializers.CharField(source='name')
    valor_adicional = serializers.DecimalField(
        source='additional_price', max_digits=10, decimal_places=2, min_value=Decimal('0.00')
    )
    ativo = serializers.BooleanField(source='is_active')

    class Meta:
        model = ProductVariation
        fields = ['id', 'produto', 'nome', 'valor_adicional', 'ativo']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='name')
    descricao = serializers.CharField(source='description', allow_blank=True, allow_null=True, required=False)
    preco_base = serializers.DecimalField(
        source='base_price', max_digits=10, decimal_places=2, min_value=Decimal('0.00')
    )
    unidade = serializers.CharField(source='unit')
    ativo = serializers.BooleanField(source='is_active')
    origem = serializers.ChoiceField(
        source='origin', choices=Product.ORIGIN_CHOICES, required=False, default='0'
    )
    cst_icms = serializers.CharField(source='icms_code', allow_blank=True, allow_null=True, required=False)
    aliquota_icms = serializers.DecimalField(
        source='icms_rate', max_digits=5, decimal_places=2,
        min_value=Decimal('0.00'), required=False, default=Decimal('0.00'),
    )
    aliquota_ipi = serializers.DecimalField(
        source='ipi_rate', max_digits=5, decimal_places=2,
        min_value=Decimal('0.00'), required=False, default=Decimal('0.00'),
    )
    aliquota_pis = serializers.DecimalField(
        source='pis_rate', max_digits=5, decimal_places=2,
        min_value=Decimal('0.00'), required=False, default=Decimal('0.00'),
    )
    aliquota_cofins = serializers.DecimalField(
        source='cofins_rate', max_digits=5, decimal_places=2,
        min_value=Decimal('0.00'), required=False, default=Decimal('0.00'),
    )
    variacoes = ProductVariationSerializer(source='variations', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'nome', 'descricao', 'preco_base', 'unidade', 'ativo',
            'variacoes', 'ncm', 'cest', 'cfop', 'origem', 'cst_icms',
            'csosn', 'aliquota_icms', 'aliquota_ipi', 'aliquota_pis',
            'aliquota_cofins', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _validate_fiscal_code(self, value, length, label):
        if not value:
            return None
        digits = ''.join(character for character in value if character.isdigit())
        if len(digits) != length:
            raise serializers.ValidationError(f'{label} deve possuir {length} dígitos.')
        return digits

    def validate_ncm(self, value):
        return self._validate_fiscal_code(value, 8, 'NCM')

    def validate_cest(self, value):
        return self._validate_fiscal_code(value, 7, 'CEST')

    def validate_cfop(self, value):
        return self._validate_fiscal_code(value, 4, 'CFOP')
