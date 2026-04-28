from rest_framework import viewsets
from .models import Pedido, PedidoItem, PedidoArquivo, PedidoHistorico
from .serializers import PedidoSerializer, PedidoItemSerializer, PedidoArquivoSerializer, PedidoHistoricoSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class PedidoItemViewSet(viewsets.ModelViewSet):
    queryset = PedidoItem.objects.all()
    serializer_class = PedidoItemSerializer

class PedidoArquivoViewSet(viewsets.ModelViewSet):
    queryset = PedidoArquivo.objects.all()
    serializer_class = PedidoArquivoSerializer

class PedidoHistoricoViewSet(viewsets.ModelViewSet):
    queryset = PedidoHistorico.objects.all()
    serializer_class = PedidoHistoricoSerializer
