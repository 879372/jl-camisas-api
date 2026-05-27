from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Pedido, PedidoHistorico

@receiver(pre_save, sender=Pedido)
def log_pedido_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Pedido.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            PedidoHistorico.objects.create(
                pedido=instance,
                acao=f"Status alterado de {old_instance.get_status_display()} para {instance.get_status_display()}",
                detalhe=f"Alteração automática de fluxo."
            )
        if old_instance.status_pagamento != instance.status_pagamento:
            PedidoHistorico.objects.create(
                pedido=instance,
                acao=f"Status de pagamento alterado de {old_instance.get_status_pagamento_display()} para {instance.get_status_pagamento_display()}",
                detalhe=f"Alteração financeira."
            )

@receiver(post_save, sender=Pedido)
def log_pedido_creation(sender, instance, created, **kwargs):
    if created:
        PedidoHistorico.objects.create(
            pedido=instance,
            acao="Pedido criado",
            detalhe=f"Pedido número {instance.numero} iniciado no sistema."
        )
