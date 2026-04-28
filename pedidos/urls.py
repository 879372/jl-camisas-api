from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, PedidoItemViewSet, PedidoArquivoViewSet, PedidoHistoricoViewSet

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet)
router.register(r'itens', PedidoItemViewSet)
router.register(r'arquivos', PedidoArquivoViewSet)
router.register(r'historico', PedidoHistoricoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
