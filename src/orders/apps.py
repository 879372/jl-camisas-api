from django.apps import AppConfig


class PedidosConfig(AppConfig):
    name = 'src.orders'

    def ready(self):
        import src.orders.signals
