from rest_framework import serializers
from .models import Produto, ProdutoVariacao

class ProdutoVariacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoVariacao
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):
    variacoes = ProdutoVariacaoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Produto
        fields = '__all__'
