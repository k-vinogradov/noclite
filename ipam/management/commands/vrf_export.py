from django.core.management.base import BaseCommand, CommandError
from ipam.models import Vrf
from optparse import make_option
from ipam.contrib import export_vrf


class Command(BaseCommand):
    help = 'Print VRF data'
    args = '<VRF name>'

    def handle(self, *args, **options):
        try:
            vrf = Vrf.objects.get(name=args[0])
        except Vrf.DoesNotExist:
            raise CommandError('VRF table "{0}" doesn\'t exist'.format(args[0]))
        self.stdout.write(export_vrf(vrf))
