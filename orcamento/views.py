from rest_framework import viewsets, permissions

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import datetime
import re
from clientes.models import Cliente
from pedidos.models import Pedido, PedidoItem

from .models import OrcamentoConfig, OrcamentoOpcao
from .serializers import OrcamentoConfigSerializer, OrcamentoOpcaoSerializer

class OrcamentoConfigViewSet(viewsets.ModelViewSet):
    queryset = OrcamentoConfig.objects.all()
    serializer_class = OrcamentoConfigSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class OrcamentoOpcaoViewSet(viewsets.ModelViewSet):
    queryset = OrcamentoOpcao.objects.all()
    serializer_class = OrcamentoOpcaoSerializer
    filterset_fields = ['categoria', 'ativo']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class CriarPedidoPublicoView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            nome = data.get('nome')
            whatsapp = data.get('whatsapp')
            valor_total = data.get('valor_total', 0)
            
            # Formata telefone apenas com numeros
            telefone_limpo = re.sub(r'\D', '', str(whatsapp))
            if len(telefone_limpo) <= 11:
                telefone_limpo = f"55{telefone_limpo}"

            # 1. Busca ou cria o cliente
            cliente = Cliente.objects.filter(telefone=telefone_limpo).first()
            if not cliente:
                cliente = Cliente.objects.create(
                    nome=nome,
                    telefone=telefone_limpo,
                    tipo='fisica'
                )

            # 2. Gera numero do pedido (ORC-YYYYMMDD-ID)
            # Para evitar concorrencia simples, usa um random ou timestamp
            # Usando ORC + Timestamp
            import time
            numero_pedido = f"ORC-{int(time.time())}"

            # 3. Cria o pedido
            pedido = Pedido.objects.create(
                numero=numero_pedido,
                cliente=cliente,
                status='orcamento',
                valor_total=valor_total
            )

            # 4. Cria o PedidoItem com as especificações
            especificacoes = {
                'quantidade': data.get('quantidade'),
                'modelo': data.get('modelo'),
                'estampa': data.get('estampa'),
                'tecido': data.get('tecido'),
                'adicionais': data.get('adicionais', []),
                'prazo': data.get('prazo')
            }
            
            # Tenta converter quantidade para decimal
            try:
                # Quantidade vem como label "50 a 100", então não dá pra usar decimal direto.
                # O banco tem max_digits=10, decimal_places=2, mas o default é 1.
                # Como a quantidade pode ser texto, vamos guardar 1 na qtde e a qtde real no JSON.
                qtd_decimal = 1
            except:
                qtd_decimal = 1

            PedidoItem.objects.create(
                pedido=pedido,
                descricao="Camisas Personalizadas - Orçamento Site",
                quantidade=qtd_decimal,
                valor_unitario=valor_total,
                valor_total=valor_total,
                especificacoes=especificacoes
            )

            return Response({'status': 'success', 'pedido': pedido.numero}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
