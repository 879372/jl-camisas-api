from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuoteConfigViewSet, QuoteOptionViewSet, CreatePublicQuoteView

router = DefaultRouter()
router.register(r'config', QuoteConfigViewSet, basename='quoteconfig')
router.register(r'opcoes', QuoteOptionViewSet, basename='quoteoption')

urlpatterns = [
    path('criar-pedido/', CreatePublicQuoteView.as_view(), name='criar_pedido'),
    path('', include(router.urls)),
]
