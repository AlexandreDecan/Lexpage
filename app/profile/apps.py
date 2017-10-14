from django.apps import AppConfig


class Config(AppConfig):
    name = 'profile'
    verbose_name = 'Profils'

    def ready(self):
        import profile.signals

