from django.apps import AppConfig


class Config(AppConfig):
    name = 'slogan'
    verbose_name = 'Slogans'

    def ready(self):
        import slogan.signals

