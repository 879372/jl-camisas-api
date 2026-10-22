from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    name = 'src.finance'

    def ready(self):
        import src.finance.signals
