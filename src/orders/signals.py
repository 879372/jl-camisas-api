from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, OrderHistory

@receiver(pre_save, sender=Order)
def log_order_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Order.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            OrderHistory.objects.create(
                order=instance,
                action=f"Status alterado de {old_instance.get_status_display()} para {instance.get_status_display()}",
                detail=f"Alteração automática de fluxo."
            )
        if old_instance.payment_status != instance.payment_status:
            OrderHistory.objects.create(
                order=instance,
                action=f"Status de pagamento alterado de {old_instance.get_payment_status_display()} para {instance.get_payment_status_display()}",
                detail=f"Alteração financeira."
            )

@receiver(post_save, sender=Order)
def log_order_creation(sender, instance, created, **kwargs):
    if created:
        OrderHistory.objects.create(
            order=instance,
            action="Pedido criado",
            detail=f"Pedido número {instance.number} iniciado no sistema."
        )
