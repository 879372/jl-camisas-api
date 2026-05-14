from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrcamentoConfigViewSet, OrcamentoOpcaoViewSet, CriarPedidoPublicoView

router = DefaultRouter()
router.register(r'config', OrcamentoConfigViewSet)
router.register(r'opcoes', OrcamentoOpcaoViewSet)

urlpatterns = [
    path('criar-pedido/', CriarPedidoPublicoView.as_view(), name='criar_pedido'),
    path('', include(router.urls)),
]
