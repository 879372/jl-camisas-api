from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'notas-fiscais', InvoiceViewSet, basename='nota-fiscal')

urlpatterns = [
    path('', include(router.urls)),
]
