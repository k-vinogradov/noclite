from django.views.generic import TemplateView
from reports.meta import REPORTS


class ReportsMainPage(TemplateView):
    template_name = 'www/reports/home.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsMainPage, self).get_context_data(**kwargs)
        context['reports'] = REPORTS
        return context
