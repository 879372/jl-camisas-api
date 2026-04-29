from rest_framework import serializers
from .models import Pedido, PedidoItem, PedidoArquivo, PedidoHistorico

class PedidoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoItem
        fields = '__all__'
        extra_kwargs = {
            'pedido': {'required': False}
        }

class PedidoArquivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoArquivo
        fields = '__all__'

class PedidoHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoHistorico
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    itens = PedidoItemSerializer(many=True, required=False)
    arquivos = PedidoArquivoSerializer(many=True, read_only=True)
    historico = PedidoHistoricoSerializer(many=True, read_only=True)
    cliente_nome = serializers.ReadOnlyField(source='cliente.nome')

    class Meta:
        model = Pedido
        fields = '__all__'

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        pedido = Pedido.objects.create(**validated_data)
        for item_data in itens_data:
            PedidoItem.objects.create(pedido=pedido, **item_data)
        return pedido

    def update(self, instance, validated_data):
        itens_data = validated_data.pop('itens', None)
        
        # Update Pedido instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update items if provided
        if itens_data is not None:
            # Simple approach: delete and recreate items
            instance.itens.all().delete()
            for item_data in itens_data:
                # Remove read-only or conflicting fields
                item_data.pop('id', None)
                item_data.pop('pedido', None)
                PedidoItem.objects.create(pedido=instance, **item_data)
        
        return instance
