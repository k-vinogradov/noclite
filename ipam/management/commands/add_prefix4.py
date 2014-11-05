from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from ipam.models import Vrf, Prefix4, STATUS_ALLOCATED, STATUS_RESERVED, STATUS_ASSIGNED
from optparse import make_option


class Command(BaseCommand):
    help = 'Add IPv4 prefix or host'
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ip', dest='prefix', help='IPv4 prefix for the network ot IP-address for the host'),
        make_option('-t', '--vrf', dest='vrf', help='VRF table name'),
        make_option('-s', '--status', dest='status',
                    choices=map(str, [STATUS_ALLOCATED, STATUS_ASSIGNED, STATUS_RESERVED]),
                    help='Prefix\'s status'),
        make_option('-f', '--domain', dest='domain', default='', help='Domain name'),
        make_option('-n', '--hostname', dest='hostname', default='', help='Host name'),
        make_option('-d', '--description', dest='description', default='', help='Description')
    )

    def handle(self, *args, **options):
        try:
            vrf = Vrf.objects.get(name=options['vrf'])
        except Vrf.DoesNotExist:
            raise CommandError('VRF table "{0}" doesn\'t exist'.format(options['vrf']))
        p = Prefix4(prefix=options['prefix'], vrf=vrf, status=unicode(options['status']),
                    domain=unicode(options['domain']), host_name=unicode(options['hostname']),
                    description=unicode(options['description']))
        try:
            p.save()
        except ValidationError as e:
            raise CommandError('. '.join(map(str,e.messages)))

        self.stdout.write('{0} successful saved.'.format(p))
