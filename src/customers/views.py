from rest_framework import viewsets
from .models import Customer
from .serializers import CustomerSerializer
from src.users.permissions import ProfileActionPermission

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at', '-id')
    serializer_class = CustomerSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve', 'create', 'update', 'partial_update'),
        'operacional': ('list', 'retrieve'),
        'financeiro': ('list', 'retrieve'),
    }
    filterset_fields = ['type', 'state']
    search_fields = ['name', 'document_number', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'updated_at']
