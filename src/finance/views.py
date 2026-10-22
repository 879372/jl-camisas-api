from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction, Invoice
from .serializers import TransactionSerializer, InvoiceSerializer
from src.users.permissions import ProfileActionPermission

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('order').all().order_by('-transaction_date', '-id')
    serializer_class = TransactionSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'financeiro': ('list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'resumo'),
        'vendas': ('list', 'retrieve', 'resumo'),
    }
    filterset_fields = ['order', 'type', 'payment_method']
    search_fields = ['description', 'order__number', 'order__customer__name']
    ordering_fields = ['transaction_date', 'amount', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        start = self.request.query_params.get('data_inicio')
        end = self.request.query_params.get('data_fim')
        if start:
            queryset = queryset.filter(transaction_date__date__gte=start)
        if end:
            queryset = queryset.filter(transaction_date__date__lte=end)
        return queryset

    @action(detail=False, methods=['get'])
    def resumo(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        totals = {
            row['type']: row['total'] or 0
            for row in queryset.values('type').annotate(total=Sum('amount'))
        }
        entries = totals.get('entrada', 0)
        exits = totals.get('saida', 0)
        return Response({'entradas': entries, 'saidas': exits, 'saldo': entries - exits})

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('order').all().order_by('-created_at', '-id')
    serializer_class = InvoiceSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'financeiro': (
            'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy',
            'exportar_xml',
        ),
        'vendas': ('list', 'retrieve', 'create'),
    }
    filterset_fields = ['order', 'type', 'status']

    @action(detail=False, methods=['get'], url_path='exportar-xml')
    def exportar_xml(self, request):
        invoices = self.filter_queryset(self.get_queryset()).exclude(xml__isnull=True).exclude(xml='')
        if not invoices.exists():
            return Response(
                {'detail': 'Nenhuma nota fiscal com XML disponível para exportação.'},
                status=404,
            )

        archive = BytesIO()
        with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as zip_file:
            for invoice in invoices:
                identifier = invoice.access_key or invoice.number or str(invoice.pk)
                safe_identifier = ''.join(char for char in identifier if char.isalnum() or char in '-_')
                zip_file.writestr(f'nfe-{safe_identifier}.xml', invoice.xml)

        response = HttpResponse(archive.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="xml-notas-fiscais.zip"'
        return response
