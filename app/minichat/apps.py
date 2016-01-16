from django.apps import AppConfig

class MinichatConfig(AppConfig):
    name = 'minichat'
    verbose_name = 'Minichat'

    def ready(self):
        import minichat.signals

