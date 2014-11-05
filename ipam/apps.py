from django.apps import AppConfig


class IpamAppConfig(AppConfig):

    name = 'ipam'
    verbose_name = 'IP Address Management'

    def ready(self):
        import ipam.signals
