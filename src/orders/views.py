from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem, OrderFile, OrderHistory
from .serializers import OrderSerializer, OrderItemSerializer, OrderFileSerializer, OrderHistorySerializer
from src.finance.models import Transaction
from src.finance.serializers import InvoiceSerializer
from src.users.permissions import ProfileActionPermission

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer').prefetch_related(
        'items', 'files', 'history'
    ).all().order_by('-created_at', '-id')
    serializer_class = OrderSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'concluir', 'dashboard'),
        'operacional': ('list', 'retrieve', 'create', 'update', 'partial_update', 'concluir', 'dashboard'),
        'financeiro': ('list', 'retrieve', 'dashboard'),
    }
    filterset_fields = ['customer', 'status', 'payment_status', 'expected_delivery_date']
    search_fields = ['number', 'customer__name', 'items__description']
    ordering_fields = ['number', 'created_at', 'updated_at', 'expected_delivery_date', 'total_amount']

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        today = timezone.localdate()
        month_start = today.replace(day=1)
        chart = []
        for months_ago in range(5, -1, -1):
            month_index = today.year * 12 + today.month - 1 - months_ago
            year, zero_based_month = divmod(month_index, 12)
            start = today.replace(year=year, month=zero_based_month + 1, day=1)
            next_index = month_index + 1
            next_year, next_zero_based_month = divmod(next_index, 12)
            end = today.replace(year=next_year, month=next_zero_based_month + 1, day=1)
            chart.append({
                'mes': start.strftime('%m/%Y'),
                'quantidade': Order.objects.filter(created_at__date__gte=start, created_at__date__lt=end).count(),
            })
        status_totals = {
            row['status']: {
                'quantidade': row['quantidade'],
                'total': row['total'] or 0,
            }
            for row in Order.objects.values('status').annotate(
                quantidade=Count('id'),
                total=Sum('total_amount'),
            )
        }
        revenue = Transaction.objects.filter(
            type='entrada', transaction_date__date__gte=month_start,
        ).aggregate(total=Sum('amount'))['total'] or 0
        pending_items = OrderItem.objects.exclude(
            order__status__in=('concluido', 'cancelado')
        ).aggregate(total=Sum('quantity'))['total'] or 0
        upcoming = Order.objects.select_related('customer').prefetch_related('items').filter(
            status__in=('orcamento', 'aguardando_pagamento', 'em_producao'),
            expected_delivery_date__isnull=False,
        ).order_by('expected_delivery_date')[:5]
        critical_count = Order.objects.filter(
            status__in=('orcamento', 'aguardando_pagamento', 'em_producao'),
            expected_delivery_date__isnull=False,
            expected_delivery_date__lte=today + timedelta(days=7),
        ).count()

        return Response({
            'por_status': status_totals,
            'faturamento_mes': revenue,
            'pedidos_mes': Order.objects.filter(created_at__date__gte=month_start).count(),
            'total_itens_pendentes': pending_items,
            'proximas_entregas': OrderSerializer(upcoming, many=True).data,
            'grafico_pedidos': chart,
            'pedidos_criticos': critical_count,
        })

    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        order = self.get_object()
        invoice_type = request.data.get('nota_fiscal', 'none')
        if invoice_type not in ('none', 'nfe', 'nfce'):
            return Response(
                {'nota_fiscal': 'Escolha none, nfe ou nfce.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            invoice_serializer = None
            if invoice_type != 'none':
                invoice_serializer = InvoiceSerializer(data={
                    'pedido': order.pk,
                    'tipo': invoice_type,
                    'status': 'pendente',
                })
                invoice_serializer.is_valid(raise_exception=True)

            order.status = 'concluido'
            order.save(update_fields=['status', 'updated_at'])
            if invoice_serializer:
                invoice_serializer.save()

        return Response(OrderSerializer(order, context={'request': request}).data)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'product').all().order_by('-id')
    serializer_class = OrderItemSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'),
        'operacional': ('list', 'retrieve', 'create', 'update', 'partial_update'),
        'financeiro': ('list', 'retrieve'),
    }
    filterset_fields = ['order', 'product']

class OrderFileViewSet(viewsets.ModelViewSet):
    queryset = OrderFile.objects.select_related('order').all().order_by('-uploaded_at', '-id')
    serializer_class = OrderFileSerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve', 'create', 'destroy'),
        'operacional': ('list', 'retrieve', 'create', 'destroy'),
        'financeiro': ('list', 'retrieve'),
    }
    filterset_fields = ['order']

class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderHistory.objects.select_related('order', 'user').all().order_by('-created_at', '-id')
    serializer_class = OrderHistorySerializer
    permission_classes = [ProfileActionPermission]
    profile_actions = {
        'vendas': ('list', 'retrieve'),
        'operacional': ('list', 'retrieve'),
        'financeiro': ('list', 'retrieve'),
    }
    filterset_fields = ['order', 'user']
