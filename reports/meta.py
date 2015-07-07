from django.core.urlresolvers import reverse

module_name = 'Reports'
module_description = 'Maintenance reports module.'
module_url_name = 'reports.home'
module_icon = 'bar-chart'
module_permissions = ['reports.view', ]

REPORTS = (
    {
        'title': u'Network Accidents',
        'description': u'',
        'url': 'reports.accidents',
        'icon': 'ambulance',
    },
)