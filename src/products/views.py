from rest_framework import viewsets
from .models import Product, ProductVariation
from .serializers import ProductSerializer, ProductVariationSerializer
from src.users.permissions import ProfileActionPermission

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('variations').all().order_by('name', 'id')
    serializer_class = ProductSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve'),
        'operacional': ('list', 'retrieve'),
        'financeiro': ('list', 'retrieve'),
    }
    filterset_fields = ['is_active', 'unit']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_price', 'created_at']

class ProductVariationViewSet(viewsets.ModelViewSet):
    queryset = ProductVariation.objects.select_related('product').all().order_by('product_id', 'name', 'id')
    serializer_class = ProductVariationSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve'),
        'operacional': ('list', 'retrieve'),
        'financeiro': ('list', 'retrieve'),
    }
    filterset_fields = ['product', 'is_active']
