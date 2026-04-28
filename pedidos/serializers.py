from rest_framework import serializers
from .models import Pedido, PedidoItem, PedidoArquivo, PedidoHistorico

class PedidoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoItem
        fields = '__all__'

class PedidoArquivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoArquivo
        fields = '__all__'

class PedidoHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoHistorico
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    itens = PedidoItemSerializer(many=True, read_only=True)
    arquivos = PedidoArquivoSerializer(many=True, read_only=True)
    historico = PedidoHistoricoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'
