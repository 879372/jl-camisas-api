from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='name')
    tipo = serializers.ChoiceField(source='type', choices=Customer.TYPE_CHOICES)
    cpf_cnpj = serializers.CharField(
        source='document_number', allow_blank=True, allow_null=True,
        required=False, validators=[],
    )
    telefone = serializers.CharField(source='phone', allow_blank=True, allow_null=True, required=False)
    cep = serializers.CharField(source='postal_code', allow_blank=True, allow_null=True, required=False)
    logradouro = serializers.CharField(source='street', allow_blank=True, allow_null=True, required=False)
    numero = serializers.CharField(source='number', allow_blank=True, allow_null=True, required=False)
    complemento = serializers.CharField(source='complement', allow_blank=True, allow_null=True, required=False)
    bairro = serializers.CharField(source='neighborhood', allow_blank=True, allow_null=True, required=False)
    cidade = serializers.CharField(source='city', allow_blank=True, allow_null=True, required=False)
    uf = serializers.CharField(source='state', allow_blank=True, allow_null=True, required=False)
    data_nascimento = serializers.DateField(source='birth_date', allow_null=True, required=False)
    observacoes = serializers.CharField(source='observations', allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'id', 'nome', 'tipo', 'cpf_cnpj', 'email', 'telefone', 'cep',
            'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'data_nascimento', 'observacoes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_cpf_cnpj(self, value):
        if not value:
            return None
        digits = ''.join(character for character in value if character.isdigit())
        if len(digits) not in (11, 14):
            raise serializers.ValidationError('Informe um CPF com 11 dígitos ou CNPJ com 14 dígitos.')
        queryset = Customer.objects.filter(document_number=digits)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Já existe um cliente com este CPF/CNPJ.')
        return digits

    def validate_uf(self, value):
        if not value:
            return value
        value = value.upper()
        if len(value) != 2:
            raise serializers.ValidationError('A UF deve ter exatamente 2 letras.')
        return value
