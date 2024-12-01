from django.apps import AppConfig


class GameTerritoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Game_Territory'

    def ready(self):
        import Game_Territory.signals