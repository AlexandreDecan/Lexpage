from django.apps import AppConfig


class BoardConfig(AppConfig):
    name = 'board'
    verbose_name = 'Discussions'

    def ready(self):
        import board.signals

