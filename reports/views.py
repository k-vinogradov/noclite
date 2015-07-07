from django.shortcuts import render
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from reports.meta import REPORTS


class ReportsMainPage(TemplateView):
    template_name = 'www/reports/home.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsMainPage, self).get_context_data(**kwargs)
        context['reports'] = REPORTS
        return context
