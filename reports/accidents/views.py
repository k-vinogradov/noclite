from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from reports.accidents.forms import *
from reports.models import NAAccident, NAUserProfile, NAConsolidationGroup
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
import re
import pytz
from datetime import datetime, time, date
from calendar import monthrange
from www.contrib import AdditionalContextViewMixin

LIST_INTERVAL = 'reports_accidents_list_interval'


class AccidentsList(FormView):
    form_class = ListDateIntervalForm
    template_name = 'www/reports/accidents/list.html'
    success_url = reverse_lazy('reports.accidents')

    def default_date_interval(self):
        tz = timezone.get_default_timezone()
        try:
            user_profile = NAUserProfile.objects.get_or_create(user=self.request.user)[0]
        except NAUserProfile.DoesNotExist():
            today = date.today()
            last_day_of_month = monthrange(today.year, today.month)[1]
            started = datetime.combine(date(today.year, today.month, 1), time(0, 0, 0, tzinfo=tz))
            finished = datetime.combine(date(today.year, today.month, last_day_of_month), time(23, 59, 59, tzinfo=tz))
        else:
            started = user_profile.accidents_list_started.astimezone(tz)
            finished = user_profile.accidents_list_finished.astimezone(tz)
        return started, finished

    def get_context_data(self, **kwargs):

        date_patterns = (
            r'^\W*(?P<year>\d{4})[.-/ ](?P<month>\d{2})[.-/ ](?P<day>\d{2})\W*$',
            r'^\W*(?P<day>\d{1,2})[.-/ ](?P<month>\d{2})[.-/ ](?P<year>\d{2}|\d{4})\W*$',
        )

        context = super(AccidentsList, self).get_context_data(**kwargs)
        context['page_title'] = u'Network Accidents'
        (started, finished) = self.default_date_interval()
        error = None
        if self.request.method == 'GET':
            if 'tz' in self.request.GET:
                if str(self.request.GET['tz']) in pytz.all_timezones:
                    tz = pytz.timezone(str(self.request.GET['tz']))
                else:
                    error = 'Wrong timezone "{0}".'.format(self.request.GET['tz'])
            else:
                tz = timezone.get_default_timezone()
            if 'started' in self.request.GET:
                m_dict = None
                for regexp in date_patterns:
                    if re.match(regexp, self.request.GET['started']):
                        m_dict = re.match(regexp, self.request.GET['started']).groupdict()
                        break
                if not m_dict:
                    error = 'Illegal date format "{0}". Use YYYY.MM.DD, D.MM.YY or D.MM.YYYY with space, ' \
                            'dash or dot as a separator.'.format(self.request.GET['started'])
                else:
                    started = datetime.combine(date(int(m_dict['year']), int(m_dict['month']), int(m_dict['day'])),
                                               time(0, 0, 0, tzinfo=tz))
            if 'finished' in self.request.GET:
                m_dict = None
                for regexp in date_patterns:
                    if re.match(regexp, self.request.GET['finished']):
                        m_dict = re.match(regexp, self.request.GET['finished']).groupdict()
                        break
                if not m_dict:
                    error = 'Illegal date format "{0}". Use YYYY.MM.DD, D.MM.YY or D.MM.YYYY with space, ' \
                            'dash or dot as a separator.'.format(self.request.GET['finished'])
                else:
                    finished = datetime.combine(date(int(m_dict['year']), int(m_dict['month']), int(m_dict['day'])),
                                                time(23, 59, 59, tzinfo=tz))
        if started > finished:
            error = 'Wrong date interval.'
        if error:
            context['error'] = error
        else:
            context['list'] = NAAccident.objects.filter(start_datetime__gte=started, start_datetime__lte=finished)
            context['list_properties'] = {'started': started, 'finished': finished, 'count': context['list'].count(),
                                          'timezone': tz}
            NAUserProfile.objects.update_or_create(
                user=self.request.user,
                defaults={'accidents_list_started': started, 'accidents_list_finished': finished})
        return context

    def get_initial(self):
        initials = super(AccidentsList, self).get_initial()
        (started, finished) = self.default_date_interval()
        if 'started' in self.request.GET:
            initials['started'] = self.request.GET['started']
        else:
            initials['started'] = started.strftime('%d.%m.%Y')
        if 'finished' in self.request.GET:
            initials['finished'] = self.request.GET['finished']
        else:
            initials['finished'] = finished.strftime('%d.%m.%Y')
        if 'tz' in self.request.GET:
            initials['tz'] = self.request.GET['tz']
        else:
            initials['tz'] = settings.TIME_ZONE
        return initials


class AccidentDetailView(DetailView):
    template_name = 'www/reports/accidents/details.html'
    model = NAAccident
    context_object_name = 'accident'

    def get_context_data(self, **kwargs):
        context = super(AccidentDetailView, self).get_context_data(**kwargs)
        context['timezone'] = timezone.get_default_timezone()
        return context


class AccidentUpdateView(UpdateView):
    model = NAAccident
    template_name = 'www/form.html'

    def get_context_data(self, **kwargs):
        context = super(AccidentUpdateView, self).get_context_data(**kwargs)
        accident = self.get_object()
        context['page_title'] = u'Update Accident #{0}'.format(accident.id)
        return context


class AccidentCreateView(CreateView, AdditionalContextViewMixin):
    model = NAAccident
    template_name = 'www/form.html'
    page_title = u'Add Network Accident'


class AccidentDeleteView(DeleteView):
    model = NAAccident
    success_url = reverse_lazy('reports.accidents')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class CGReport(FormView):
    template_name = 'www/reports/accidents/cg.html'
    form_class = ConsolidationReportForm
    success_url = reverse_lazy('reports.accidents.cg')

    def get_context_data(self, **kwargs):
        context = super(CGReport, self).get_context_data(**kwargs)
        if 'start' in self.request.GET and 'finish' in self.request.GET and 'tz' in self.request.GET:
            tz = pytz.timezone(self.request.GET['tz'])
            context['list_properties'] = {'timezone': tz}
            d1 = datetime.strptime(self.request.GET['start'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
            d2 = datetime.strptime(self.request.GET['finish'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
            context['report'] = [obj.report(d1, d2) for obj in NAConsolidationGroup.objects.all()]
        return context

    def get_initial(self):
        initials = super(CGReport, self).get_initial()
        if self.request.method == 'GET':
            if 'start' in self.request.GET and 'finish' in self.request.GET and 'tz' in self.request.GET:
                initials['start'] = datetime.strptime(self.request.GET['start'], '%Y-%m-%d %H:%M:%S')
                initials['finish'] = datetime.strptime(self.request.GET['finish'], '%Y-%m-%d %H:%M:%S')
                initials['tz'] = self.request.GET['tz']
        return initials

    def form_valid(self, form):
        from django.utils.http import urlquote

        data = form.clean()
        return redirect(
            '{0}?{1}'.format(self.success_url, '&'.join(['{0}={1}'.format(k, urlquote(data[k])) for k in data])))