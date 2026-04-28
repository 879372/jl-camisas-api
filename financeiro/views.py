from rest_framework import viewsets
from .models import Lancamento, NotaFiscal
from .serializers import LancamentoSerializer, NotaFiscalSerializer

class LancamentoViewSet(viewsets.ModelViewSet):
    queryset = Lancamento.objects.all()
    serializer_class = LancamentoSerializer

class NotaFiscalViewSet(viewsets.ModelViewSet):
    queryset = NotaFiscal.objects.all()
    serializer_class = NotaFiscalSerializer
