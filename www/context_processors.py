from django.core.urlresolvers import reverse
from www.forms import SearchForm


def main_menu(request):
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'
    context = {'BASE_URL': scheme + request.get_host(), 'search_form': SearchForm()}

    module = request.path.split('/')[1]
    sub_module = request.path.split('/')[2] if len(request.path.split('/')) > 2 else ''
    if module == 'ipam':
        if request.user.has_module_perms('ipam'):
            context['main_menu'] = {
                'module_title': 'IP Address Management',
                'menu': [
                    {
                        'icon': 'fa-cloud',
                        'caption': u'VRF Tables',
                        'url': reverse('ipam.vrf_list'),
                        'active': True if sub_module == 'vrf' else False
                    }, {
                        'icon': 'fa-globe',
                        'caption': u'Domains Service',
                        'url': reverse('ipam.home'),
                        'active': True if sub_module == 'ipv4' else False
                    }, {
                        'icon': 'fa-info-circle',
                        'caption': u'Reports',
                        'url': reverse('ipam.reports'),
                        'active': True if sub_module == 'reports' else False},
                ]}
        else:
            context['main_menu'] = {
                'module_title': 'IP Address Management',
                'menu': [], }
    elif module == 'reports':
        if request.user.has_module_perms('reports'):
            context['main_menu'] = {
                'module_title': 'Reports',
                'menu': [
                    {
                        'icon': 'fa-ambulance',
                        'caption': u'Network Accidents',
                        'url': reverse('reports.accidents'),
                        'active': True if sub_module == 'accidents' else False},
                ]
            }
        else:
            context['main_menu'] = {
                'module_title': 'Reports',
                'menu': [], }
    else:
        context['main_menu'] = {
            'module_title': 'Network Operations Center Lite',
            'menu': {},
        }
    return context


