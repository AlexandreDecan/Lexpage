from django.apps import AppConfig

class SloganConfig(AppConfig):
    name = 'slogan'
    verbose_name = 'Slogans'

    def ready(self):
        import slogan.signals

