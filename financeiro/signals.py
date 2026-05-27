from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lancamento
from pedidos.models import Pedido
from django.db.models import Sum

@receiver([post_save, post_delete], sender=Lancamento)
def update_pedido_payment_status(sender, instance, **kwargs):
    if instance.pedido:
        pedido = instance.pedido
        # Calculate total paid for this order (only entries)
        total_pago = Lancamento.objects.filter(
            pedido=pedido, 
            tipo='entrada'
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        pedido.valor_pago = total_pago
        
        # Update status_pagamento
        if pedido.valor_pago >= pedido.valor_total:
            pedido.status_pagamento = 'pago'
        elif pedido.valor_pago > 0:
            pedido.status_pagamento = 'parcial'
        else:
            pedido.status_pagamento = 'pendente'
            
        pedido.save()
