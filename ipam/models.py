# -*- coding: utf-8 -*-

import re

from math import ceil

from ipcalc import Network
from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

STATUS_ALLOCATED = u'allocated'
STATUS_ASSIGNED = u'assigned'
STATUS_RESERVED = u'reserved'

BLOCK_STATUSES = [STATUS_ALLOCATED, STATUS_RESERVED]


class Vrf(models.Model):
    """
    Stores a single VRF table entry, related to :model:`ipam.Prefix4`
    """
    name = models.SlugField(max_length=64, verbose_name=u'name', unique=True, help_text=u'VRF name')
    rd = models.CharField(max_length=16, verbose_name=u'route-distinguisher', unique=True,
                          help_text=u'Route Distinguisher')
    description = models.TextField(verbose_name=u'description', blank=True)

    class Meta:
        ordering = ['name', ]
        verbose_name = u'VRF'
        verbose_name_plural = u'VRFs'
        permissions = (
            ('view', 'Can view IPAM module content'),
        )

    def __str__(self):
        return 'VRF ' + self.name

    def __unicode__(self):
        return unicode(self.__str__())

    def prefixes(self, root_only=False, networks_only=False, hosts_only=False, statuses=None, subnet=None):
        """
        Return QuerySet with VRF's prefixes
        :param root_only: return top-level's prefixes only
        :type root_only: bool
        :param networks_only: return networks only (without hosts)
        :type networks_only: bool
        :param hosts_only: return hosts only (without networks)
        :type hosts_only: bool
        :param statuses: statuses list for filter
        :type statuses: list
        :return: QuerySet
        :rtype: django.db.models.QuerySet
        """
        args = {}
        if statuses:
            args['status__in'] = statuses
        if root_only:
            args['parent'] = None
        if networks_only:
            args['size__gt'] = 1
        elif hosts_only:
            args['size'] = 1
        if subnet:
            network = Network(subnet)
            args['first_ip_dec__gte'] = network.ip
            args['last_ip_dec__lte'] = network.broadcast_long()
        return self.prefixes_list if len(args) == 0 else self.prefixes_list.filter(**args)

    def networks(self):
        return self.prefixes(networks_only=True)

    def networks_root(self):
        return self.prefixes(networks_only=True, root_only=True)

    def hosts(self):
        return self.prefixes(hosts_only=True)

    def hosts_root(self):
        return self.prefixes(hosts_only=True, root_only=True)

    def size_total(self):
        r = self.prefixes(root_only=True).aggregate(sum_size=models.Sum('size'))['sum_size']
        return r if r else 0

    def size_reserved(self):
        r = self.prefixes(statuses=[STATUS_RESERVED, ]).aggregate(sum_size=models.Sum('size'))['sum_size']
        return r if r else 0

    def size_allocated(self):
        r = self.prefixes(statuses=[STATUS_ALLOCATED, ]).aggregate(sum_size=models.Sum('size'))['sum_size']
        return r if r else 0

    def size_free(self):
        return self.size_total() - self.size_allocated() - self.size_reserved()

    def fqdn(self, ip):
        ip = Network(ip)
        prefix = self.prefixes().filter(first_ip_dec__lte=ip.ip, last_ip_dec__gte=ip.ip, size__gte=ip.size()).last()
        return prefix.fqdn() if prefix else None

    def delete(self, *args, **kwargs):
        for prefix in self.prefixes().all():
            prefix.delete()
        super(Vrf, self).delete(*args, **kwargs)

    def journal(self):
        from www.models import Journal

        return Journal.objects.by_objects(self)

    def get_absolute_url(self):
        return reverse('ipam.vrf_detail', kwargs={'slug': self.name, })

    def get_update_url(self):
        return reverse('ipam.vrf_update', kwargs={'slug': self.name, })

    def get_delete_url(self):
        return reverse('ipam.vrf_delete', kwargs={'slug': self.name, })

    def clean(self):
        super(Vrf, self).clean()
        if self.name[:3] == u'vrf':
            raise ValidationError(u'"vrf..." is bad name for the VRF')

    def save(self, user=None, *args, **kwargs):
        message = None
        if user:
            if self.id:
                p = Vrf.objects.get(id=self.id)
                message = u'User {0} ({1}) modified VRF {2}'.format(user.profile.get_short_name(), user.email,
                                                                    self.name)
                if p.name != self.name:
                    message += u' New name: "{0}".'.format(self.name)
                if p.rd != self.rd:
                    message += u' New RD: {0}'.format(self.rd)
                if p.description != self.description:
                    message += u' New description: "{0}"'.format(self.description)
            else:
                message = u'User {0} ({1}) create VRF table {2}'.format(user.profile.get_short_name(), user.email,
                                                                        self.name)
        super(Vrf, self).save(*args, **kwargs)
        if message and user:
            from www.models import Journal
            from www.constatnts import JL_INFO

            Journal.objects.create(level=JL_INFO, message=message, objects=[self, user])


class Prefix4Manager(models.Manager):
    def by_vrf(self, vrf, networks_only=False, hosts_only=False):
        if networks_only:
            return self.filter(vrf=vrf, size__gt=1)
        elif hosts_only:
            return self.filter(vrf=vrf, size=1)
        else:
            return self.filter(vrf=vrf)


class Prefix4(models.Model):
    STATUSES = (
        (STATUS_ALLOCATED, u'Allocated'),
        (STATUS_ASSIGNED, u'Assigned'),
        (STATUS_RESERVED, u'Reserved'),
    )
    vrf = models.ForeignKey('Vrf', verbose_name=u'VRF', related_name='prefixes_list')

    prefix = models.CharField(verbose_name=u'IP Address', max_length=18)
    size = models.IntegerField(verbose_name=u'subnet size', blank=True, null=True)
    description = models.TextField(verbose_name=u'description', blank=True)
    status = models.CharField(verbose_name=u'Status', max_length=64, choices=STATUSES, default=STATUS_ASSIGNED)
    parent = models.ForeignKey('self', verbose_name=u'parent', related_name='child', blank=True, null=True,
                               on_delete=models.SET_NULL)
    domain = models.CharField(max_length=255, verbose_name=u'domain', blank=True)
    host_name = models.CharField(max_length=255, verbose_name=u'host name', blank=True)

    sequence_number = models.FloatField(blank=True, null=True)
    first_ip_dec = models.IntegerField(blank=True, null=True)
    last_ip_dec = models.IntegerField(blank=True, null=True)

    objects = Prefix4Manager()

    class Meta:
        ordering = ['sequence_number', ]
        unique_together = ('vrf', 'prefix')
        verbose_name = 'IPv4 prefix'
        verbose_name_plural = u'IPv4 Prefixes'

    def __str__(self):
        if self.size == 1:
            return u'Host {0} [vrf:{1}]'.format(self.ip, self.vrf.name)
        else:
            return u'Prefix {0} [vrf:{1}]'.format(self.prefix, self.vrf.name)

    def __unicode__(self):
        return unicode(self.__str__())

    def length(self):
        return int(self.prefix.split('/')[1])

    def vrf_list(self, exclude_self=False):
        if self.id and exclude_self:
            return Prefix4.objects.by_vrf(self.vrf).exclude(id=self.id)
        else:
            return Prefix4.objects.by_vrf(self.vrf)

    def full_domain(self):
        if self.domain and self.domain[-1] == u'.':
            return self.domain
        elif self.domain:
            return u'{0}.{1}'.format(self.domain, self.parent.full_domain() if self.parent else '')
        else:
            return self.parent.full_domain() if self.parent else ''

    def fqdn(self):
        if self.host_name:
            return self.host_name if self.host_name[-1] == u'.' else (self.host_name + u'.' + self.full_domain())
        else:
            return self.full_domain()

    def prefixes_lower(self, root_only=False, networks_only=False, hosts_only=False, statuses=None,
                       ignore_stored_values=False):
        if self.id and root_only and not ignore_stored_values:
            args = {}
            if networks_only:
                args['size__gt'] = 1
            elif hosts_only:
                args['size'] = 1
            if statuses:
                args['status__in'] = statuses
            return self.child if len(args) == 0 else self.child.filter(**args)

        network = Network(str(self.prefix))
        f_ip = network.ip
        l_ip = network.broadcast_long()
        qs = self.vrf.prefixes(
            networks_only=networks_only,
            hosts_only=hosts_only,
            statuses=statuses).filter(first_ip_dec__gte=f_ip, last_ip_dec__lte=l_ip)
        if ignore_stored_values:
            # TODO Add check with ignoring stored data
            pass
        else:
            if self.id:
                qs = qs.exclude(id=self.id)
            if root_only:
                return qs.filter(parent=self.find_parent())
            else:
                return qs

    def prefixes_upper(self, networks_only=False, hosts_only=False, statuses=None):
        network = Network(str(self.prefix))
        f_ip = network.ip
        l_ip = network.broadcast_long()
        if self.id:
            return self.vrf.prefixes(networks_only=networks_only, hosts_only=hosts_only, statuses=statuses).filter(
                first_ip_dec__lte=f_ip, last_ip_dec__gte=l_ip, size__gt=network.size()).exclude(id=self.id)
        else:
            return self.vrf.prefixes(networks_only=networks_only, hosts_only=hosts_only, statuses=statuses).filter(
                first_ip_dec__lte=f_ip, last_ip_dec__gte=l_ip, size__gt=network.size())

    def find_parent(self):
        return self.prefixes_upper(networks_only=True).last()

    def networks(self):
        return self.prefixes_lower(root_only=True, networks_only=True)

    def networks_root(self):
        return self.networks()

    def networks_recursive(self):
        return self.prefixes_lower(networks_only=True)

    def hosts(self):
        return self.prefixes_lower(root_only=True, hosts_only=True)

    def hosts_root(self):
        return self.hosts()

    def hosts_recursive(self):
        return self.prefixes_lower(hosts_only=True)

    def size_total(self):
        return self.size

    def size_allocated(self):
        if self.status == STATUS_ALLOCATED:
            return self.size_total()
        else:
            r = self.prefixes_lower(statuses=[STATUS_ALLOCATED]).aggregate(sum_size=models.Sum('size'))['sum_size']
            return r if r else 0

    def size_reserved(self):
        if self.status == STATUS_RESERVED:
            return self.size_total()
        else:
            r = self.prefixes_lower(statuses=[STATUS_RESERVED]).aggregate(sum_size=models.Sum('size'))['sum_size']
            return r if r else 0

    def size_free(self):
        return self.size - self.size_allocated() - self.size_reserved()

    def allocated_percents(self):
        return int(ceil(float(self.size_allocated()) / float(self.size_total()) * 100))

    def reserved_percents(self):
        return int(ceil(float(self.size_reserved()) / float(self.size_total()) * 100))

    def free_percents(self):
        return 100 - self.allocated_percents() - self.reserved_percents()

    def journal(self):
        from www.models import Journal

        return Journal.objects.by_objects(self)

    @property
    def ip(self):
        return Network(self.prefix).dq

    def get_absolute_url(self):
        return reverse('ipam.prefix4_detail', kwargs={'slug': self.prefix, 'vrf': self.vrf.name, })

    def get_update_url(self):
        if self.size == 1:
            return reverse('ipam.prefix4_update', kwargs={'vrf': self.vrf.name, 'slug': self.ip, })
        else:
            return reverse('ipam.prefix4_update', kwargs={'vrf': self.vrf.name, 'slug': self.prefix, })

    def get_delete_url(self):
        return reverse('ipam.prefix4_delete', kwargs={'slug': self.prefix, 'vrf': self.vrf.name, })

    def clean(self):
        super(Prefix4, self).clean()
        prefix = self.prefix
        if re.match(r'(\d{1,3}\.){3}\d{1,3}[\s]*$', prefix):
            self.prefix = prefix + '/32'
        elif re.match(r'(\d{1,3}\.){3}\d{1,3}/\d{1,2}', prefix):
            pass
        else:
            raise ValidationError(u'Invalid network prefix "{0}"'.format(prefix))
        network = Network(str(self.prefix))

        if network.network().dq != network.dq:
            raise ValidationError(u'Invalid prefix length /{0}'
                                  u' for the network {1}'.format(self.prefix.split('/')[1], self.prefix.split('/')[0]))

        # qs = self.vrf_list(exclude_self=True)

        if not self.find_parent() and not self.domain:
            ValidationError(u'Top-level prefix must have domain name')

        if self.status in BLOCK_STATUSES:
            p = self.prefixes_lower(statuses=BLOCK_STATUSES).first()
            if not p:
                p = self.prefixes_upper(statuses=BLOCK_STATUSES).last()
            if p:
                raise ValidationError(u'Network {0} is already {1}'.format(p.prefix, p.get_status_display().lower()))

    def save(self, recursion=True, user=None, *args, **kwargs):
        self.full_clean()
        network = Network(str(self.prefix))
        self.size = network.size()
        self.first_ip_dec = network.ip
        self.last_ip_dec = self.first_ip_dec + long(self.size) - 1
        self.sequence_number = self.first_ip_dec + self.length() * 0.01
        self.parent = self.find_parent()

        if self.size == 1:
            self.domain = ''

        old_data = None
        message = None

        if user:
            if self.id:
                old_data = {
                    'prefix': self.prefix,
                    'description': self.description,
                    'status': self.status,
                    'domain': self.domain,
                    'host_name': self.host_name,
                }
            else:
                message = u'User {user} ({email}) create prefix {prefix}. Status: {status}.'.format(
                    user=user.profile.get_short_name(), email=user.email, prefix=self.__str__(), status=self.status)
                if self.description:
                    message += u' Description: {0}.'.format(self.description)
                if self.domain:
                    message += u' Domain: {0}.'.format(self.domain)
                if self.host_name:
                    message += u' Hostname: {0}.'.format(self.host_name)

        super(Prefix4, self).save(*args, **kwargs)

        if user:
            from www.models import Journal
            from www.constatnts import JL_INFO

            if old_data:
                message = u'User {user} ({email}) updated prefix {prefix}.'.format(user=user.profile.get_short_name(),
                                                                                   email=user.email,
                                                                                   prefix=self.__str__())
                if self.status != old_data[u'status']:
                    message += u' Status was changed from "{0}" to "{1}".'.format(old_data['status'], self.status)
                if self.description != old_data[u'description']:
                    message += u' New description: "{0}".'.format(self.description)
                if self.domain != old_data[u'domain']:
                    message += u' Domain was changed from "{0}" to "{1}".'.format(old_data['domain'], self.domain)
                if self.host_name != old_data[u'host_name']:
                    message += u' Hostname was changed from "{0}" to "{1}".'.format(old_data['host_name'],
                                                                                    self.host_name)
            Journal.objects.create(level=JL_INFO, message=message, objects=[user, self, ])

        if recursion:
            for p in self.prefixes_lower():
                print 'Check {0}'.format(p)
                print p.find_parent()
                print p.parent
                if p.find_parent() != p.parent:
                    p.save(recursion=False)

    def delete(self, using=None):
        child_prefix_ids = [p.id for p in self.child.all()]
        super(Prefix4, self).delete(using=using)
        for p_id in child_prefix_ids:
            Prefix4.objects.get(id=p_id).save()