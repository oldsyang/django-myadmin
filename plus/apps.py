from django.apps import AppConfig



class PlusConfig(AppConfig):
    name = 'plus'

    def ready(self):
        super().ready()

        from django.utils.module_loading import autodiscover_modules

        autodiscover_modules("pl")
