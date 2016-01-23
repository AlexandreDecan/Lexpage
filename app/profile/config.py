from django.apps import AppConfig

class ProfileConfig(AppConfig):
    name = 'profile'
    verbose_name = 'Profils'

    def ready(self):
        import profile.signals

