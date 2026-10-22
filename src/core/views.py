from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint para verificação de integridade do sistema (Health Check).
    Verifica se a conexão com o banco de dados está ativa.
    """
    try:
        connection.ensure_connection()
        return Response({
            "status": "ok", 
            "database": "connected",
            "message": "Sistema JL Camisas está online."
        })
    except Exception as e:
        return Response({
            "status": "error", 
            "database": "disconnected",
            "error": str(e)
        }, status=503)

