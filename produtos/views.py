from rest_framework import viewsets
from .models import Produto, ProdutoVariacao
from .serializers import ProdutoSerializer, ProdutoVariacaoSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.filter(ativo=True)
    serializer_class = ProdutoSerializer

class ProdutoVariacaoViewSet(viewsets.ModelViewSet):
    queryset = ProdutoVariacao.objects.filter(ativo=True)
    serializer_class = ProdutoVariacaoSerializer
