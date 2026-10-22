from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import QuoteConfig, QuoteOption
from .serializers import QuoteConfigSerializer, QuoteOptionSerializer
from .services import QuoteService
from src.users.permissions import ProfileActionPermission

class QuoteConfigViewSet(viewsets.ModelViewSet):
    queryset = QuoteConfig.objects.all().order_by('id')
    serializer_class = QuoteConfigSerializer
    profile_actions = {
        'vendas': ('create', 'update', 'partial_update'),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [ProfileActionPermission()]

    def perform_create(self, serializer):
        if QuoteConfig.objects.exists():
            raise ValidationError({'detail': 'A configuração geral já foi criada.'})
        serializer.save()

class QuoteOptionViewSet(viewsets.ModelViewSet):
    queryset = QuoteOption.objects.all()
    serializer_class = QuoteOptionSerializer
    filterset_fields = ['category', 'is_active']
    profile_actions = {
        'vendas': ('create', 'update', 'partial_update', 'destroy'),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        active = self.request.query_params.get('ativo')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() in ('1', 'true', 'sim'))
        elif not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [ProfileActionPermission()]


class CreatePublicQuoteView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'public_quote'

    def post(self, request):
        try:
            order_number = QuoteService.create_public_quote(request.data)
            return Response({'status': 'success', 'pedido': order_number}, status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Não foi possível criar o orçamento.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
