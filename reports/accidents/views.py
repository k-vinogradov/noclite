# -*- coding: utf-8 -*-

from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from reports.accidents.forms import *
from reports.models import NAAccident, NAUserProfile, NAConsolidationGroup
from django.utils import timezone
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
import re
import pytz
from datetime import datetime, time, date
from calendar import monthrange
from www.contrib import AdditionalContextViewMixin, JournalViewMixin

LIST_INTERVAL = 'reports_accidents_list_interval'
START_DATE_GET_ATTRIBUTE = 'started'
FINISH_DATE_GET_ATTRIBUTE = 'finished'
TIMEZONE_GET_ATTRIBUTE = 'tz'

DATE_PATTERNS = (
    r'^\W*(?P<year>\d{4})[.-/ ](?P<month>\d{2})[.-/ ](?P<day>\d{2})\W*$',
    r'^\W*(?P<day>\d{1,2})[.-/ ](?P<month>\d{2})[.-/ ](?P<year>\d{2}|\d{4})\W*$',
)


class AccidentsList(FormView):
    form_class = ListDateIntervalForm
    template_name = 'www/reports/accidents/list.html'
    success_url = reverse_lazy('reports.accidents')

    def render_to_response(self, context, **response_kwargs):
        if 'error' in context or 'export' not in self.request.GET:
            return super(AccidentsList, self).render_to_response(context, **response_kwargs)
        else:
            import io
            from xlsxwriter.workbook import Workbook

            columns_formats = [
                {'index': 0, 'title': u'хТТК/zТТК', 'width': 13},
                {'index': 1, 'title': u'Город', 'width': 15},
                {'index': 2, 'title': u'Дата и время (МСК) начала аварии', 'width': 16},
                {'index': 3, 'title': u'Дата и время (МСК) завершения аварии', 'width': 16},
                {'index': 4, 'title': u'Длительность аварии', 'width': 13},
                {'index': 5, 'title': u'Категория аварии', 'width': 10},
                {'index': 6, 'title': u'Вид аварии', 'width': 31},
                {'index': 7, 'title': u'Узел, место (адрес) объекта', 'width': 24},
                {'index': 8, 'title': u'Количество ЗКЛ', 'width': 11},
                {'index': 9, 'title': u'Причина аварии', 'width': 20},
                {'index': 10, 'title': u'Выполненные АВР', 'width': 23},
            ]

            output = io.BytesIO()
            workbook = Workbook(output, {'in_memory': True})

            header_format = workbook.add_format(
                properties={
                    #'bold': True,
                    'bg_color': 'yellow',
                    'border_color': 'black',
                    'border': 1,
                    'text_wrap': True,
                    'valign': 'top'})
            text_wrap = workbook.add_format(properties={'text_wrap': True, 'valign': 'top'})
            # header_format.set_bold()
            #header_format.set_bg_color('yellow')
            #header_format.set_border_color('black')

            worksheet = workbook.add_worksheet(u'Аварии')
            worksheet.write_row(0, 0, [col['title'] for col in columns_formats], header_format)
            for col in columns_formats:
                worksheet.set_column(col['index'], col['index'], col['width'])
            row_index = 1
            for obj in context['list']:
                accident = obj
                """:type : NAAccident """
                if accident.is_completed():
                    worksheet.write_row(row_index, 0, [
                        accident.companies_list(),
                        accident.cities_list(),
                        accident.start_datetime.astimezone(context['list_properties']['timezone']).strftime(
                            '%d.%m.%Y %H:%M'),
                        accident.finish_datetime.astimezone(context['list_properties']['timezone']).strftime(
                            '%d.%m.%Y %H:%M'),
                        accident.duration_max_str(),
                        accident.category.title,
                        accident.kind.__unicode__(),
                        accident.locations,
                        accident.affected_customers,
                        accident.reason,
                        accident.actions
                    ], text_wrap)
                row_index += 1

            workbook.close()
            output.seek(0)
            response = HttpResponse(output.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'attachment; filename="Accident list.xlsx"'
            return response

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
        context = super(AccidentsList, self).get_context_data(**kwargs)
        context['page_title'] = u'Network Accidents'
        (started, finished) = self.default_date_interval()
        error = None
        if self.request.method == 'GET':
            if TIMEZONE_GET_ATTRIBUTE in self.request.GET:
                if str(self.request.GET[TIMEZONE_GET_ATTRIBUTE]) in pytz.all_timezones:
                    tz = pytz.timezone(str(self.request.GET[TIMEZONE_GET_ATTRIBUTE]))
                else:
                    error = 'Wrong timezone "{0}".'.format(self.request.GET[TIMEZONE_GET_ATTRIBUTE])
            else:
                tz = timezone.get_default_timezone()
            if START_DATE_GET_ATTRIBUTE in self.request.GET:
                m_dict = None
                for regexp in DATE_PATTERNS:
                    if re.match(regexp, self.request.GET[START_DATE_GET_ATTRIBUTE]):
                        m_dict = re.match(regexp, self.request.GET[START_DATE_GET_ATTRIBUTE]).groupdict()
                        break
                if not m_dict:
                    error = 'Illegal date format "{0}". Use YYYY.MM.DD, D.MM.YY or D.MM.YYYY with space, ' \
                            'dash or dot as a separator.'.format(self.request.GET[START_DATE_GET_ATTRIBUTE])
                else:
                    started = datetime.combine(date(int(m_dict['year']), int(m_dict['month']), int(m_dict['day'])),
                                               time(0, 0, 0, tzinfo=tz))
            if FINISH_DATE_GET_ATTRIBUTE in self.request.GET:
                m_dict = None
                for regexp in DATE_PATTERNS:
                    if re.match(regexp, self.request.GET[FINISH_DATE_GET_ATTRIBUTE]):
                        m_dict = re.match(regexp, self.request.GET[FINISH_DATE_GET_ATTRIBUTE]).groupdict()
                        break
                if not m_dict:
                    error = 'Illegal date format "{0}". Use YYYY.MM.DD, D.MM.YY or D.MM.YYYY with space, ' \
                            'dash or dot as a separator.'.format(self.request.GET[FINISH_DATE_GET_ATTRIBUTE])
                else:
                    finished = datetime.combine(date(int(m_dict['year']), int(m_dict['month']), int(m_dict['day'])),
                                                time(23, 59, 59, tzinfo=tz))
        if started > finished:
            error = 'Wrong date interval.'
        if error:
            context['error'] = error
        else:
            context['list'] = NAAccident.objects.filter(start_datetime__range=(started, finished))
            context['list_properties'] = {'started': started, 'finished': finished, 'count': context['list'].count(),
                                          'timezone': tz}
            NAUserProfile.objects.update_or_create(
                user=self.request.user,
                defaults={'accidents_list_started': started, 'accidents_list_finished': finished})
        return context

    def get_initial(self):
        initials = super(AccidentsList, self).get_initial()
        (started, finished) = self.default_date_interval()
        if START_DATE_GET_ATTRIBUTE in self.request.GET:
            initials['started'] = self.request.GET[START_DATE_GET_ATTRIBUTE]
        else:
            initials['started'] = started.strftime('%d.%m.%Y')
        if FINISH_DATE_GET_ATTRIBUTE in self.request.GET:
            initials['finished'] = self.request.GET[FINISH_DATE_GET_ATTRIBUTE]
        else:
            initials['finished'] = finished.strftime('%d.%m.%Y')
        if TIMEZONE_GET_ATTRIBUTE in self.request.GET:
            initials['tz'] = self.request.GET[TIMEZONE_GET_ATTRIBUTE]
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


class AccidentUpdateView(AdditionalContextViewMixin, JournalViewMixin, UpdateView):
    model = NAAccident
    template_name = 'www/form.html'
    page_title = u'Update Accident'


class AccidentCreateView(AdditionalContextViewMixin, JournalViewMixin, CreateView):
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