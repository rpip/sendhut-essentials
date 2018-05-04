from django.apps import AppConfig


class StoresConfig(AppConfig):
    name = 'sendhut.stores'
    verbose_name = "Lunch"

    def ready(self):
        import sendhut.stores.signals  # noqa
