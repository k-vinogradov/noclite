from ipcalc import Network, IP

from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from ipam.models import Vrf, Prefix4, Domain4
from ipam.forms import *

from www.contrib import AddUserInstanceViewMixin


class VrfListView(ListView):
    model = Vrf
    template_name = 'www/ipam/vrf-list.html'


class VrfDetailView(DetailView):
    model = Vrf
    template_name = 'www/ipam/vrf-detail.html'
    slug_field = 'name'

    def get_context_data(self, **kwargs):
        context = super(VrfDetailView, self).get_context_data(**kwargs)
        context['breadcrumb'] = [
            {'url': reverse_lazy('ipam.vrf_list'), 'caption': u'IPAM'},
            {'url': None, u'caption': 'VRF: {0}'.format(self.get_object().name)}, ]
        context['page_title'] = u'VRF Table: {0} '.format(self.get_object().name)
        return context


class VrfCreateView(AddUserInstanceViewMixin, CreateView):
    model = Vrf
    template_name = 'www/form.html'

    def get_context_data(self, **kwargs):
        context = super(VrfCreateView, self).get_context_data(**kwargs)
        context['page_title'] = u'Create VRF Table'
        return context


class VrfUpdateView(AddUserInstanceViewMixin, UpdateView):
    model = Vrf
    template_name = 'www/form.html'
    slug_field = 'name'

    def get_context_data(self, **kwargs):
        context = super(VrfUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = u'Update VRF <a href="{0}">{1}</a>'.format(self.get_object().get_absolute_url(),
            self.get_object().name)
        return context


class VrfDeleteView(DeleteView):
    model = Vrf
    success_url = reverse_lazy('ipam.vrf_list')
    slug_field = 'name'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class Prefix4DeleteView(DeleteView):
    model = Prefix4
    slug_field = 'prefix'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_queryset(self):
        return Vrf.objects.get(name=self.kwargs['vrf']).prefixes()

    def get_success_url(self):
        if self.object.parent:
            return self.object.parent.get_absolute_url()
        else:
            return self.object.vrf.get_absolute_url()


class Prefix4Detail(DetailView):
    model = Prefix4
    template_name = 'www/ipam/prefix-detail.html'
    slug_field = 'prefix'

    def get_queryset(self):
        return Vrf.objects.get(name=self.kwargs['vrf']).prefixes()

    def get_context_data(self, **kwargs):
        context = super(Prefix4Detail, self).get_context_data(**kwargs)
        prefix = self.get_object()
        if prefix.size == 1:
            context['page_title'] = u'Host {0} Detail'.format(prefix.ip)
        else:
            context['page_title'] = u'Network {0} Detail'.format(prefix.prefix)
        context['breadcrumb'] = [
            {'url': reverse_lazy('ipam.vrf_list'), 'caption': u'IPAM'},
            {'url': prefix.vrf.get_absolute_url(), 'caption': u'VRF: {0}'.format(prefix.vrf.name)}, ]
        for pp in prefix.prefixes_upper():
            context['breadcrumb'].append({
                'url': pp.get_absolute_url(),
                'caption': pp.prefix
            })
        context['breadcrumb'].append({
            'url': None,
            'caption': prefix.ip if prefix.size == 1 else prefix.prefix,
        })
        return context


class Prefix4CreateView(CreateView):
    model = Prefix4
    template_name = 'www/form.html'
    page_title = u''

    def get_initial(self):
        init = super(Prefix4CreateView, self).get_initial()
        init['vrf'] = Vrf.objects.get(name=self.kwargs['vrf'])
        if self.request.method == 'GET' and 'prefix' in self.request.GET:
            init['prefix'] = self.request.GET['prefix']
        return init

    def form_valid(self, form):
        instance = self.model(**form.cleaned_data)
        instance.save(user=self.request.user)
        return redirect(instance.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super(Prefix4CreateView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class Prefix4NetCreateView(Prefix4CreateView):
    fields = ['vrf', 'prefix', 'description', 'status', 'domain', 'host_name']
    page_title = u'Create Network'


class Prefix4HostCreateView(Prefix4CreateView):
    fields = ['vrf', 'prefix', 'description', 'status', 'host_name', ]
    page_title = u'Create Host'


class Prefix4UpdateView(UpdateView):
    model = Prefix4
    template_name = 'www/form.html'
    slug_field = 'prefix'

    def form_valid(self, form):
        cd = form.cleaned_data
        instance = self.get_object()
        for key in cd:
            setattr(instance, key, cd[key])
        instance.save(user=self.request.user)
        return redirect(instance.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super(Prefix4UpdateView, self).get_context_data(**kwargs)
        p = self.get_object()
        t = 'Host' if p.size == 1 else 'Network'
        context['page_title'] = u'Update {0} {1}'.format(t, p.prefix)
        return context


class Prefix4NetUpdateView(Prefix4UpdateView):
    fields = ['vrf', 'prefix', 'description', 'status', 'domain', 'host_name']

    def get_queryset(self):
        return Vrf.objects.get(name=self.kwargs['vrf']).prefixes()


class Prefix4HostUpdateView(Prefix4UpdateView):
    fields = ['vrf', 'prefix', 'description', 'status', 'host_name', ]

    def get_object(self, queryset=None):
        p_object = Vrf.objects.get(name=self.kwargs['vrf']).prefixes().get(prefix=self.kwargs['slug'] + '/32')
        if '/' in p_object.prefix:
            p_object.prefix = p_object.prefix.split('/')[0]
        return p_object


class FreeBlocks4ReportView(FormView):
    form_class = FreeBlocks4ReportForm
    template_name = 'www/ipam/free-blocks-4.html'
    success_url = reverse_lazy('ipam.report_free4')

    def get_context_data(self, **kwargs):
        from django.db.models import Sum
        from ipam.models import BLOCK_STATUSES

        def search_free(vrf, network, statuses):
            """
            Free blocks recursive search
            :param vrf: VRF
            :type vrf: Vrf
            :param network:  Network
            :type network: Network
            """
            f_ip = network.ip
            l_ip = network.broadcast_long()
            size = network.size()
            blocked_size = \
                vrf.prefixes().filter(status__in=statuses, first_ip_dec__gte=f_ip, last_ip_dec__lte=l_ip).aggregate(
                    sum_size=Sum('size'))['sum_size']
            if not blocked_size:
                blocked_size = 0
            if size == blocked_size:
                return []
            elif blocked_size == 0:
                if vrf.prefixes().filter(first_ip_dec__lte=f_ip, last_ip_dec__gte=l_ip):
                    parent = vrf.prefixes().filter(first_ip_dec__lte=f_ip, last_ip_dec__gte=l_ip).last()
                else:
                    parent = None
                if size == 1:
                    create_url = '{0}?prefix={1}'.format(reverse_lazy('ipam.host4_add', kwargs={'vrf': vrf.name}),
                                                         network.dq)
                else:
                    create_url = '{0}?prefix={1}'.format(reverse_lazy('ipam.prefix4_add', kwargs={'vrf': vrf.name}),
                                                         network)
                return [{'prefix': str(network), 'parent': parent, 'create_url': create_url}]
            else:
                net_1 = Network('{0}/{1}'.format(network.to_tuple()[0], network.to_tuple()[1] + 1))
                net_2 = Network('{0}/{1}'.format(IP(net_1.broadcast_long() + 1).dq, network.subnet() + 1))
                return search_free(vrf, net_1, statuses) + search_free(vrf, net_2, statuses)

        context = super(FreeBlocks4ReportView, self).get_context_data(**kwargs)
        context['page_title'] = u'Free IPv4 Blocks'
        if 'vrf' in self.request.GET and 'prefix' in self.request.GET:
            if Vrf.objects.filter(name=self.request.GET['vrf']):
                net = Network(self.request.GET['prefix'])
                if net.dq != net.network():
                    net = Network('{0}/{1}'.format(net.network(), net.subnet()))
                context['report'] = search_free(Vrf.objects.get(name=self.request.GET['vrf']), net, BLOCK_STATUSES)
                context['total'] = len(context['report'])
        return context

    def form_valid(self, form):
        vrf = form.cleaned_data['vrf']
        prefix = form.cleaned_data['prefix']
        self.success_url = '{url}?vrf={vrf}&prefix={prefix}'.format(url=reverse_lazy('ipam.report_free4'), vrf=vrf.name,
                                                                    prefix=prefix)
        return super(FreeBlocks4ReportView, self).form_valid(form)

    def get_initial(self):
        initials = super(FreeBlocks4ReportView, self).get_initial()
        if self.request.method == 'GET':
            if 'vrf' in self.request.GET and Vrf.objects.filter(name=self.request.GET['vrf']):
                initials['vrf'] = Vrf.objects.get(name=self.request.GET['vrf'])
            if 'prefix' in self.request.GET:
                initials['prefix'] = self.request.GET['prefix']
        return initials


class ReportsView(TemplateView):
    template_name = 'www/ipam/reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        context['reports'] = [
            {'name': u'Free blocks IPv4', 'url': reverse_lazy('ipam.report_free4')}
        ]
        context['page_title'] = u'IPAM Reports'
        return context


class Domain4ZoneView(TemplateView):
    template_name = 'www/ipam/reverse-zone.html'

    def get_context_data(self, **kwargs):
        context = super(Domain4ZoneView, self).get_context_data(**kwargs)
        if 'zone' in self.request.GET:
            context['object'] = Domain4.objects.get(zone=self.request.GET['zone'])
        return context