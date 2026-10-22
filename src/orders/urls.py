from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, OrderFileViewSet, OrderHistoryViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'items', OrderItemViewSet, basename='orderitem')
router.register(r'files', OrderFileViewSet, basename='orderfile')
router.register(r'history', OrderHistoryViewSet, basename='orderhistory')

urlpatterns = [
    path('', include(router.urls)),
]
