from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

import www.views as www
import ipam.views as ipam
import reports.views as reports
import reports.accidents.views as reports_accidents
import reports.accidents.api as accidents_api

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'noclite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', www.HomeView.as_view(), name='home'),

    url(r'^search/$', www.SearchView.as_view(), name='search'),

    url(r'^sign-in/$', 'django.contrib.auth.views.login',
        {'template_name': 'www/authentication/login.html'}, name='login'),
    url(r'^sign-out/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^password-change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^password-change-done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^password-reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password-reset-done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^password-reset-confirm/(?P<uidb64>.*)/(?P<token>.*)/$', 'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^password-reset-complete/$', 'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),

    # Search
    # url(r'^search/')

    # IPAM
    url(r'ipam/$', permission_required(['ipam.view', ])(ipam.VrfListView.as_view()), name='ipam.home'),
    url(r'ipam/vrf/$', permission_required(['ipam.view', ])(ipam.VrfListView.as_view()), name='ipam.vrf_list'),

    url(r'ipam/vrf-create/$', permission_required(['ipam.view', 'ipam.add_vrf'])(ipam.VrfCreateView.as_view()),
        name='ipam.vrf_add'),
    url(r'ipam/vrf-(?P<slug>[-_\w]+)/$', permission_required(['ipam.view', ])(ipam.VrfDetailView.as_view()),
        name='ipam.vrf_detail'),
    url(r'ipam/vrf-(?P<slug>[-_\w]+)/update/$',
        permission_required(['ipam.view', 'ipam.change_vrf'])(ipam.VrfUpdateView.as_view()),
        name='ipam.vrf_update'),
    url(r'ipam/vrf-(?P<slug>[-_\w]+)/delete/$',
        permission_required(['ipam.view', 'ipam.delete_vrf'])(ipam.VrfDeleteView.as_view()),
        name='ipam.vrf_delete'),

    url(r'ipam/vrf-(?P<vrf>[-_\w]+)/(?P<slug>(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?)/$',
        permission_required(['ipam.view', ])(ipam.Prefix4Detail.as_view()),
        name='ipam.prefix4_detail'),
    url(r'ipam/vrf-(?P<vrf>[-_\w]+)/network-add/$',
        permission_required(['ipam.view', 'ipam.add_prefix4'])(ipam.Prefix4NetCreateView.as_view()),
        name='ipam.prefix4_add'),
    url(r'ipam/vrf-(?P<vrf>[-_\w]+)/host-add/$',
        permission_required(['ipam.view', 'ipam.add_prefix4'])(ipam.Prefix4HostCreateView.as_view()),
        name='ipam.host4_add'),
    url(r'ipam/vrf-(?P<vrf>[-_\w]+)/(?P<slug>(\d{1,3}\.){3}\d{1,3}/\d{1,2})/update/$',
        permission_required(['ipam.view', 'ipam.add_prefix4'])(ipam.Prefix4NetUpdateView.as_view()),
        name='ipam.prefix4_update'),
    url(r'ipam/vrf-(?P<vrf>[-_\w]+)/(?P<slug>(\d{1,3}\.){3}\d{1,3})/update/$',
        permission_required(['ipam.view', 'ipam.change_prefix4'])(ipam.Prefix4HostUpdateView.as_view()),
        name='ipam.prefix4_update'),
    url(r'ipam/vrf-(?P<vrf>[-_\w]+)/(?P<slug>(\d{1,3}\.){3}\d{1,3}/\d{1,2})/delete/$',
        permission_required(['ipam.view', 'ipam.delete_prefix4'])(ipam.Prefix4DeleteView.as_view()),
        name='ipam.prefix4_delete'),

    url(r'ipam/reports/$',
        permission_required(['ipam.view', ])(ipam.ReportsView.as_view()),
        name='ipam.reports'),
    url(r'ipam/reports/free-blocks/$',
        permission_required(['ipam.view', ])(ipam.FreeBlocks4ReportView.as_view()),
        name='ipam.report_free4'),

    url(r'ipam/domains/$', ipam.Domain4ZoneView.as_view(), name='ipam.domain'),
    url(r'ipam/domain-list/$', ipam.Domain4List.as_view(), name='ipam.domain_list'),

    # REPORTS MODULE
    url(r'reports/$', permission_required(['reports.view', ])(reports.ReportsMainPage.as_view()), name='reports.home'),

    # Accidents Report
    url(r'reports/accidents/$', permission_required(['reports.view_na', ])(reports_accidents.AccidentsList.as_view()),
        name='reports.accidents'),
    url(r'reports/accidents/(?P<pk>\d+)$',
        permission_required(['reports.view_na', ])(reports_accidents.AccidentDetailView.as_view()),
        name='reports.accidents.detail'),
    url(r'reports/accidents/(?P<pk>\d+)/update$',
        permission_required(['reports.change_naaccident', ])(reports_accidents.AccidentUpdateView.as_view()),
        name='reports.accidents.update'),
    url(r'reports/accidents/add/$',
        permission_required(['reports.add_naaccident', ])(reports_accidents.AccidentCreateView.as_view()),
        name='reports.accidents.add'),
    url(r'reports/accidents/(?P<pk>\d+)/delete$',
        permission_required(['reports.delete_naaccident', ])(reports_accidents.AccidentDeleteView.as_view()),
        name='reports.accidents.delete'),

    url(r'reports/accidents/cg/$', permission_required(['reports.view_cg'])(reports_accidents.CGReport.as_view()),
        name='reports.accidents.cg'),

    # API
    url(r'api/reports/accidents/references/$', csrf_exempt(accidents_api.GetReferencesAPI.as_view()),
        name='api.reports.accidents.references'),
    url(r'api/reports/accidents/update/$', csrf_exempt(accidents_api.UpdateAPI.as_view()),
        name='api.reports.accidents.update'),

)
