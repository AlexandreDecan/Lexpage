from django.apps import AppConfig


class AldpConfig(AppConfig):
    name = 'aldp'
    verbose_name = 'A La Demande Populaire'

    def ready(self):
        import aldp.signals

