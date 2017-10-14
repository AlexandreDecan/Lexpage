from django.apps import AppConfig


class Config(AppConfig):
    name = 'board'
    verbose_name = 'Discussions'

    def ready(self):
        import board.signals

