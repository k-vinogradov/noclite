# -*- coding: utf-8 -*-

import re
from ipam.models import Vrf, Prefix4
from ipcalc import Network
from django.db.models import Q


def search(user, search_args):
    """

    :param user: User
    :type user: django.contrib.auth.models.User
    :param search_args: String list
    :type search_args: list
    :return: List of results: {title, utl, description, module}
    """
    if not user.has_perms(['ipam.view', ]):
        return []
    else:
        ip = None
        string_args = []
        ip_reg_exp = re.compile('(\d{1,3}\.)\d{1,3}(/\d{1,3})?')
        for line in search_args:
            if ip_reg_exp.match(line) and not ip:
                ip = line if '/' in line else line + '/32'
            else:
                string_args.append(line)

        objects = []

        # Search Prefix4
        qs = Prefix4.objects.all()
        if ip:
            network = Network(ip)
            f_ip = network.ip
            l_ip = network.broadcast_long()
            qs = qs.filter(first_ip_dec__lte=f_ip, last_ip_dec__gte=l_ip)
            for s in string_args:
                qs = qs.filter(Q(description__icontains=s) | Q(status__icontains=s) | Q(domain__icontains=s) | Q(
                    host_name__icontains=s))
            if qs:
                objects.append(qs.last())
        qs = Prefix4.objects.all()
        for s in search_args:
            qs = qs.filter(Q(description__icontains=s) | Q(status__icontains=s) | Q(domain__icontains=s) | Q(
                host_name__icontains=s) | Q(prefix__icontains=s))
        for prefix in qs:
            if prefix not in objects:
                objects.append(prefix)

        qs = Vrf.objects.all()
        for s in search_args:
            qs = qs.filter(Q(description__icontains=s) | Q(rd__icontains=s) | Q(name__icontains=s))
        for vrf in qs:
            if vrf not in objects:
                objects.append(vrf)

        return [{'title': str(o), 'url': o.get_absolute_url(), 'description': o.description, 'module': 'IPAM'} for o in
                objects]


def export_vrf(vrf):
    """
    Export data to the text
    :param vrf: VRF
    :type vrf: ipam.models.Vrf
    :return: Text
    :rtype: str
    """

    def prefix_line(prefix4):
        """

        :param prefix4: Prefix
        :type prefix4: ipam.model.Prefix4
        :return: Text line
        :rtype: str
        """
        return u'{prefix}\t{status}\tdomain:{domain}\thost:{host_name}\t{description}'.format(
            prefix=Prefix4.ip if prefix4.size == 1 else prefix4.prefix,
            status=prefix4.status,
            domain=prefix4.domain,
            host_name=prefix4.host_name,
            description=prefix4.description)

    return u'[GENERAL]\n' \
           u'name="{name}"\n' \
           u'rd={rd}\n' \
           u'description="{description}"\n\n' \
           u'[IPv4 PREFIXES]\n' \
           u'{prefixes}'.format(name=vrf.name, rd=vrf.rd, description=vrf.description,
                               prefixes=u'\n'.join([prefix_line(p) for p in vrf.prefixes().all()]))