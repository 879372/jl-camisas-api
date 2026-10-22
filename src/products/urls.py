from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductVariationViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variations', ProductVariationViewSet, basename='productvariation')

urlpatterns = [
    path('', include(router.urls)),
]
