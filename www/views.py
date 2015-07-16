# -*- coding: utf-8 -*-

from www.forms import SearchForm
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class HomeView(TemplateView):
    template_name = 'www/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['page_title'] = 'Network Operations Center Lite'
        modules = []
        for module_name in settings.NOCL_MODULES:
            module_name += '.meta'
            module = __import__(module_name)
            components = module_name.split('.')
            for comp in components[1:]:
                module = getattr(module, comp)
            try:
                if self.request.user.has_perms(module.module_permissions):
                    modules.append({
                        'title': module.module_name,
                        'description': module.module_description,
                        'url': reverse_lazy(module.module_url_name),
                        'icon': module.module_icon, })
            except AttributeError:
                continue
        context['modules'] = modules
        return context


class SearchView(FormView):
    template_name = 'www/search.html'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        from re import split

        context = super(SearchView, self).get_context_data(**kwargs)
        context['page_title'] = 'Global Search'
        context['hide_header_form'] = True
        results = []
        if self.request.method == 'GET' and 'search_string' in self.request.GET:
            args = split(r'\s+', urlsafe_base64_decode(self.request.GET['search_string']))
            for module_name in settings.NOCL_MODULES:
                module_name += '.meta'
                module = __import__(module_name)
                components = module_name.split('.')
                for comp in components[1:]:
                    module = getattr(module, comp)
                try:
                    func = module.search_func
                except AttributeError:
                    continue
                results += func(user=self.request.user, search_args=args)
        if len(results) > 0:
            context['results'] = results
        return context

    def get_success_url(self):
        return '{0}?search_string={1}'.format(reverse_lazy('search'),
                                              urlsafe_base64_encode(
                                                  self.request.POST['search_string'].encode('utf-8').strip()))

    def get_initial(self):
        initial = super(SearchView, self).get_initial()
        if self.request.method == 'GET' and 'search_string' in self.request.GET:
            initial['search_string'] = urlsafe_base64_decode(self.request.GET['search_string'])
        return initial