from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LancamentoViewSet, NotaFiscalViewSet

router = DefaultRouter()
router.register(r'lancamentos', LancamentoViewSet)
router.register(r'notas-fiscais', NotaFiscalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
