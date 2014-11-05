from django.apps import AppConfig


class WwwAppConfig(AppConfig):
    name = 'www'
    verbose_name = 'Web Inerface'

    def ready(self):
        import signals