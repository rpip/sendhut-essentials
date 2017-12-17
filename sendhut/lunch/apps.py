from django.apps import AppConfig


class LunchConfig(AppConfig):
    name = 'sendhut.lunch'
    verbose_name = "Lunch"

    def ready(self):
        import sendhut.lunch.signals  # noqa
