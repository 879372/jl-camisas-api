from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction
from src.orders.models import Order
from django.db.models import Sum

@receiver([post_save, post_delete], sender=Transaction)
def update_order_payment_status(sender, instance, **kwargs):
    if instance.order:
        order = instance.order
        total_paid = Transaction.objects.filter(
            order=order,
            type='entrada'
        ).aggregate(total=Sum('amount'))['total'] or 0

        order.paid_amount = total_paid

        if order.paid_amount >= order.total_amount:
            order.payment_status = 'pago'
        elif order.paid_amount > 0:
            order.payment_status = 'parcial'
        else:
            order.payment_status = 'pendente'

        order.save()
