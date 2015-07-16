from django.apps import AppConfig


class ReportsAppConfig(AppConfig):

    name = 'reports'
    verbose_name = 'NOC Lite Reports'

    def ready(self):
        import reports.signals
