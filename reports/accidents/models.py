from datetime import datetime, timedelta, time

from django.core import serializers
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from www.contrib import NamedModel, ActiveAble, JournalMixin

NA_SCHEDULE_WH = 'WH'
NA_SCHEDULE_24H = '24'
NA_SCHEDULES = (
    (NA_SCHEDULE_WH, u'During the working hours'),
    (NA_SCHEDULE_24H, u'Around the Clock')
)


class NASettingsException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return u'Network Accidents Error: {0}'.format(self.msg)

    def __repr__(self):
        return self.__str__()


class NACompany(NamedModel, ActiveAble):
    class Meta(NamedModel.Meta):
        verbose_name = u'company'
        verbose_name_plural = u'companies'


class NACity(NamedModel, ActiveAble):
    class Meta(NamedModel.Meta):
        verbose_name = u'city'
        verbose_name_plural = u'cities'


class NARegion(NamedModel, ActiveAble):
    cities = models.ManyToManyField('NACity', verbose_name=u'Cities', limit_choices_to=ActiveAble.limit_choice())

    class Meta(NamedModel.Meta):
        verbose_name = u'region'
        verbose_name_plural = u'regions'

    def cities_str(self):
        return u', '.join([obj.name for obj in self.cities.filter(is_active=True)])


class NACategory(ActiveAble):
    COLOURS = (
        ('default', 'Default',),
        ('primary', 'Primary'),
        ('success', 'Success'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    )

    number = models.IntegerField(unique=True, verbose_name=u'Number')
    title = models.CharField(max_length=4, verbose_name=u'Caption')
    description = models.TextField(blank=True, verbose_name=u'Description')
    color = models.CharField(max_length=8, choices=COLOURS, verbose_name=u'Label color')

    class Meta(NamedModel.Meta):
        ordering = ['number', ]
        verbose_name = u'category'
        verbose_name_plural = u'categories'

    def __unicode__(self):
        return self.title if self.id else u'New Category'

    def html_label(self):
        return '<span class="label label-{0}">{1}</span>'.format(self.color, self.title)


class NAKind(ActiveAble):
    code = models.CharField(max_length=8, unique=True, verbose_name=u'Code')
    title = models.CharField(max_length=255, verbose_name=u'Title')
    description = models.TextField(blank=True, verbose_name=u'Description')

    class Meta:
        ordering = ['code', 'title', ]
        verbose_name = u'kind of accident'
        verbose_name_plural = u'kinds of accident'

    def __unicode__(self):
        return u'{0}. {1}'.format(self.code, self.title) if self.id else u'New Kind of Accident'


class NAAccident(models.Model, JournalMixin):
    companies = models.ManyToManyField('NACompany', null=True, blank=True, verbose_name=u'Company',
                                       limit_choices_to=ActiveAble.limit_choice())
    cities = models.ManyToManyField('NACity', null=True, blank=True, verbose_name=u'City',
                                    limit_choices_to=ActiveAble.limit_choice())
    start_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'Begining time')
    finish_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'Finish time')
    category = models.ForeignKey('NACategory', blank=True, null=True, verbose_name=u'Category',
                                 limit_choices_to=ActiveAble.limit_choice())
    kind = models.ForeignKey('NAKind', blank=True, null=True, verbose_name=u'Kind',
                             limit_choices_to=ActiveAble.limit_choice())
    locations = models.TextField(blank=True, null=True, verbose_name=u'Locations')
    affected_customers = models.IntegerField(blank=True, null=True, verbose_name=u'Number of affected customers')
    magistral_customers_affected = models.BooleanField(blank=True, default=False,
                                                       verbose_name=u'Magistral customers affected')
    reason = models.TextField(blank=True, null=True, verbose_name=u'Cause of accident')
    actions = models.TextField(blank=True, null=True, verbose_name=u'Emergency actions')
    iss_id = models.IntegerField(blank=True, null=True, verbose_name=u'ISS emergency job\'s number')
    consolidation_report_ignore_cause = models.TextField(blank=True, default=u'',
                                                         verbose_name=u'Cause of ignoring accident in the consolidation'
                                                                      u' report')

    class Meta:
        ordering = ['start_datetime', 'finish_datetime', ]
        verbose_name = u'accident'
        verbose_name_plural = u'accidents'
        permissions = (
            ('view', 'Can view network accidents'),
            ('view_na', 'Can view network accidents details'),
        )

    def __unicode__(self):
        if self.id:
            return u'Accident #{0} (ISS-{1})'.format(self.id, self.iss_id) if self.iss_id else u'Accident #{0}'.format(
                self.id)
        else:
            return u'New Accident'

    def clean(self):
        super(NAAccident, self).clean()
        if self.start_datetime and self.finish_datetime:
            if self.finish_datetime < self.start_datetime:
                raise ValidationError(u'The accident can\'t be finished earlier thant it\'s been started.')

    def journal(self):
        from www.models import Journal

        return Journal.objects.by_objects(self)

    def get_absolute_url(self):
        return reverse('reports.accidents.detail', kwargs={'pk': self.id}) if self.id else None

    def get_update_url(self):
        return reverse('reports.accidents.update', kwargs={'pk': self.id}) if self.id else None

    def companies_list(self):
        return ', '.join([item.name for item in self.companies.all()])

    def cities_list(self):
        return ', '.join([item.name for item in self.cities.all()])

    def is_completed(self):
        if not (self.category and self.kind):
            return False
        elif not (self.start_datetime and self.finish_datetime and self.locations and self.affected_customers):
            return False
        elif not (self.reason and self.actions and self.iss_id):
            return False
        elif self.companies.count() == 0 or self.cities.count() == 0:
            return False
        else:
            return True

    def kind_and_category_string(self):
        if self.category and self.kind:
            return u'{0} ({1})'.format(self.kind, self.category)
        elif self.category:
            return u'N/A ({0})'.format(self.category)
        elif self.kind:
            return u'{0} (N/A)'.format(self.kind)
        else:
            return u'N/A'

    def regions(self):
        return NARegion.actives.filter(cities__in=self.cities.all())

    def accident_durations(self):
        rl = self.regions()
        if not self.is_completed():
            return dict((r, 0) for r in rl)
        try:
            working_hours = NAWorkHours.objects.get(category=self.category, kind=self.kind)
        except NAWorkHours.DoesNotExist:
            try:
                working_hours = NAWorkHours.objects.get(category=self.category, kind=None)
            except NAWorkHours.DoesNotExist:
                raise NASettingsException(
                    u'couldn\'t find an appropriate schedule for accident "{0}"'.format(
                        self.kind_and_category_string()))
        if self.magistral_customers_affected:
            schedule = working_hours.magistral_affected_schedule
        else:
            schedule = working_hours.main_schedule
        if schedule == NA_SCHEDULE_24H:
            duration = (self.finish_datetime - self.start_datetime).total_seconds() / 60
            return dict((r, duration) for r in rl)
        result = dict((r, 0) for r in rl)
        day = timedelta(days=1)
        tz = timezone.get_default_timezone()
        current_datetime = self.start_datetime.astimezone(tz)
        finish_datetime = self.finish_datetime.astimezone(tz)
        while current_datetime < finish_datetime:
            current_date = current_datetime.date()
            for r in rl:
                try:
                    type_of_day = NADay.objects.get(region=r, date=current_date).day_type
                except NADay.DoesNotExist:
                    try:
                        type_of_day = NADay.objects.get(region=None, date=current_date).day_type
                    except NADay.DoesNotExist:
                        try:
                            if current_date.weekday() < 5:
                                type_of_day = NADayType.objects.get(region=r, default_workday=True)
                            else:
                                type_of_day = NADayType.objects.get(region=r, default_day_off=True)
                        except NADayType.DoesNotExist:
                            try:
                                if current_date.weekday() < 5:
                                    type_of_day = NADayType.objects.get(region=None, default_workday=True)
                                else:
                                    type_of_day = NADayType.objects.get(region=None, default_day_off=True)
                            except NADayType.DoesNotExist:
                                raise NASettingsException(
                                    u'couldn\'t find an appropriate type of day for {0} region "{1}"'.format(
                                        current_date, r))
                if type_of_day.start and type_of_day.finish:
                    t_1 = current_datetime.time() if current_datetime.time() > type_of_day.start else type_of_day.start

                    if current_datetime.date() == finish_datetime.date():
                        end_of_accident = finish_datetime.time()
                    else:
                        end_of_accident = time(23, 59, 59)
                    t_2 = end_of_accident if end_of_accident < type_of_day.finish else type_of_day.finish
                    if t_2 > t_1:
                        result[r] += int((t_2.hour - t_1.hour) * 60 +
                                         (t_2.minute - t_1.minute) +
                                         (t_2.second - t_1.second) / 60)

            current_datetime = timezone.make_aware(
                datetime.combine(date=current_datetime.date() + day, time=time(0, 0, 0)),
                timezone.get_default_timezone())
        return result

    def duration_max(self):
        if not self.is_completed():
            return 0
        duration = 0
        durations = self.accident_durations()
        for region in durations:
            if durations[region] > duration:
                duration = durations[region]
        return duration

    def duration_max_str(self):
        minutes = self.duration_max()
        return timedelta(minutes=minutes).__str__()[:-3] if minutes > 0 else u''

    def accident_duration_str(self):
        expired = self.is_expired_by_region()
        durations = self.accident_durations()
        return [
            {'region': key,
             'duration': timedelta(minutes=durations[key]).__str__()[:-3] if durations[key] > 0 else u'',
             'is_expired': expired[key]} for key in durations
            ]

    def _time_limit(self):
        if not self.is_completed():
            return 1000000
        try:
            time_limit_obj = NATimeLimit.objects.get(category=self.category, kind=self.kind)
        except NATimeLimit.DoesNotExist:
            try:
                time_limit_obj = NATimeLimit.objects.get(category=self.category, kind=None)
            except NATimeLimit.DoesNotExist:
                raise NASettingsException(
                    u'Could\'t find time limit for category {0} and kind of accident "{1}"'.format(self.category,
                                                                                                   self.kind))
        if self.magistral_customers_affected:
            return time_limit_obj.magistral_affected_limit
        else:
            return time_limit_obj.main_limit

    def is_expired_by_region(self):
        if not self.is_completed():
            return dict((r, False) for r in self.regions())
        time_limit = self._time_limit()
        durations = self.accident_durations()
        return dict((r, durations[r] > time_limit) for r in durations)

    def is_expired(self):
        return self.duration_max() > self._time_limit()

    def overtime(self):
        time_limit = self._time_limit()
        if self.duration_max() > time_limit:
            return self.duration_max() - time_limit
        else:
            return 0

    def overtime_str(self):
        return timedelta(minutes=self.overtime()).__str__()[:-3]

    def json(self):
        return serializers.serialize('json', [self, ])


class NADayType(NamedModel):
    start = models.TimeField(verbose_name=u'Start', null=True, blank=True)
    finish = models.TimeField(verbose_name=u'Finish', null=True, blank=True)
    default_workday = models.BooleanField(blank=True, default=False, verbose_name=u'Default workday')
    default_day_off = models.BooleanField(blank=True, default=False, verbose_name=u'Default day off')
    region = models.ForeignKey('NARegion', null=True, blank=True, verbose_name=u'Region',
                               limit_choices_to=ActiveAble.limit_choice())

    class Meta(NamedModel.Meta):
        verbose_name = u'type of a day'
        verbose_name_plural = u'types of a day'

    def default_settings(self):
        if self.default_workday:
            return 'Default workday'
        elif self.default_day_off:
            return 'Default day off'
        else:
            return ''

    def clean(self):
        super(NADayType, self).clean()
        if self.finish < self.start:
            raise ValidationError(u'Finish time can\'t be earlier than start one.')


class NADay(models.Model):
    date = models.DateField(verbose_name=u'Date')
    day_type = models.ForeignKey('NADayType', verbose_name=u'Type of day')
    region = models.ForeignKey('NARegion', null=True, blank=True, verbose_name=u'Region',
                               limit_choices_to=ActiveAble.limit_choice())

    class Meta:
        ordering = ['date', ]
        verbose_name = u'day'
        verbose_name_plural = u'days'

    def __unicode__(self):
        return self.date.strftime('%d.%m.%Y') if self.id else u'New Day'


class NAWorkHours(models.Model):
    category = models.ForeignKey('NACategory', verbose_name=u'Category of accident',
                                 limit_choices_to=ActiveAble.limit_choice())
    kind = models.ForeignKey('NAKind', null=True, blank=True, verbose_name=u'Kind of accident',
                             limit_choices_to=ActiveAble.limit_choice())
    main_schedule = models.CharField(max_length=4, choices=NA_SCHEDULES, verbose_name=u'Schedule')
    magistral_affected_schedule = models.CharField(max_length=4, choices=NA_SCHEDULES,
                                                   verbose_name=u'Schedule if magistral customers was affected')

    class Meta:
        ordering = ['kind', 'category', ]
        verbose_name = u'schedule'
        verbose_name_plural = u'schedules'

    def __unicode__(self):
        if self.kind:
            return u'{0} ({1})'.format(self.kind, self.category) if self.id else u'New schedule'
        else:
            return u'Any kind ({1})'.format(self.kind, self.category) if self.id else u'New schedule'


class NATimeLimit(models.Model):
    category = models.ForeignKey('NACategory', verbose_name=u'Category of accident',
                                 limit_choices_to=ActiveAble.limit_choice())
    kind = models.ForeignKey('NAKind', blank=True, null=True, verbose_name=u'Kind of accident',
                             limit_choices_to=ActiveAble.limit_choice())
    main_limit = models.IntegerField(verbose_name=u'Time limit (min)')
    magistral_affected_limit = models.IntegerField(verbose_name=u'Schedule if magistral customers was affected (min)')

    class Meta:
        ordering = ['category', 'kind', ]
        verbose_name = u'time limit'
        verbose_name_plural = u'time limits'

    def __unicode__(self):
        if self.id:
            return u'{0} ({1})'.format(self.kind if self.kind else 'Any kind', self.category)
        else:
            return u'New Time Limit'


class NAUserProfilesManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        from datetime import date
        from calendar import monthrange

        if self.filter(**kwargs).exists():
            return super(NAUserProfilesManager, self).get_or_create(*args, **kwargs)
        else:
            new_kwagrs = kwargs.copy()
            tz = timezone.get_default_timezone()
            today = date.today()
            last_day_of_onth = monthrange(today.year, today.month)[1]
            if 'accidents_list_started' not in new_kwagrs:
                new_kwagrs['accidents_list_started'] = datetime.combine(date(today.year, today.month, 1),
                                                                        time(0, 0, 0, tzinfo=tz))
            if 'accidents_list_finished' not in new_kwagrs:
                new_kwagrs['accidents_list_finished'] = datetime.combine(
                    date(today.year, today.month, last_day_of_onth),
                    time(23, 59, 59, tzinfo=tz))
            return super(NAUserProfilesManager, self).get_or_create(*args, **new_kwagrs)


class NAUserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name=u'User', unique=True)
    accidents_list_started = models.DateTimeField(verbose_name=u'Start datetime for accidents list')
    accidents_list_finished = models.DateTimeField(verbose_name=u'Finish datetime for accidents list')

    objects = NAUserProfilesManager()


class NAKindCategoryMap(models.Model):
    kinds = models.ManyToManyField('NAKind', verbose_name=u'Kinds of accidents',
                                   limit_choices_to=ActiveAble.limit_choice())
    categories = models.ManyToManyField('NACategory', verbose_name=u'Categories',
                                        limit_choices_to=ActiveAble.limit_choice())
    ignore_kinds = models.ManyToManyField('NAKind', related_name='ignore_nakind_set',
                                          verbose_name=u'Ignore',
                                          help_text=u'Ignore expired check for accidents, which have this kinds.',
                                          limit_choices_to=ActiveAble.limit_choice(), blank=True, null=True)
    ignore_categories = models.ManyToManyField('NACategory', related_name='ignore_nacategory_set',
                                               verbose_name=u'Ignore',
                                               help_text=u'Ignore expired check for accidents, which have this '
                                                         u'categories.',
                                               limit_choices_to=ActiveAble.limit_choice(), blank=True, null=True)
    consolidation_group = models.ForeignKey('NAConsolidationGroup')

    def clean(self):
        super(NAKindCategoryMap, self).clean()
        if self.id:
            for k in self.ignore_kinds.all():
                if k not in self.kinds.all():
                    ValidationError('Kind list must contain every item from "expired-ignore" list')
            for c in self.ignore_categories.all():
                if c not in self.categories.all():
                    ValidationError('Category list must contain every item from "expired-ignore" list')

    def accidents(self, **kwargs):
        kwargs['kind__in'] = self.kinds.all()
        kwargs['category__in'] = self.categories.all()
        return NAAccident.objects.filter(**kwargs).distinct()

    def expired_ignored_accidents(self, **kwargs):
        params = {}
        if self.ignore_kinds.count() > 0:
            params['kind__in'] = self.ignore_kinds.all()
        if self.ignore_categories.count() > 0:
            params['category__in'] = self.ignore_categories.all()
        if len(params) == 0:
            params['kind__in'] = []
            params['category__in'] = []

        return self.accidents(**kwargs).filter(**params)


class NAConsolidationGroup(NamedModel):
    regions = models.ManyToManyField('NARegion', verbose_name=u'Regions for consolidation',
                                     limit_choices_to=ActiveAble.limit_choice())
    companies = models.ManyToManyField('NACompany', verbose_name=u'Companies',
                                       limit_choices_to=ActiveAble.limit_choice())

    class Meta(NamedModel.Meta):
        verbose_name = u'consolidation groups'
        verbose_name_plural = u'consolidation groups'
        permissions = (('view_cg', "Can view accidents consolidation report"),)

    def cities(self):
        return NACity.objects.filter(naregion__in=self.regions.all())

    def accidents(self, started=None, finished=None, ignored=False):
        params = {'cities__in': self.cities(), 'companies__in': self.companies.all(),
                  'consolidation_report_ignore_cause': u''}
        if started:
            params['start_datetime__gte'] = started
        if finished:
            params['start_datetime__lte'] = finished
        accidents_id = []
        for cmap in self.nakindcategorymap_set.all():
            if ignored:
                accidents_id += [a.id for a in cmap.expired_ignored_accidents(**params) if a.is_completed()]
            else:
                accidents_id += [a.id for a in cmap.accidents(**params) if a.is_completed()]
        params['id__in'] = accidents_id
        return NAAccident.objects.filter(**params).distinct()

    def report(self, start_datetime, finish_datetime):
        cat_id = []
        for cmap in self.nakindcategorymap_set.all():
            cat_id += [c.id for c in cmap.categories.all()]
        result = {
            'title': self.name,
            'total': {'ontime': 0, 'expired': 0, 'total': 0},
            'accidents': [],
            'cities': self.cities(),
            'regions': self.regions.all(),
            'companies': self.companies.all(),
            'maps': [
                {'kinds': obj.kinds.all(),
                 'categories': obj.categories.all(),
                 'i_kinds': obj.ignore_kinds.all(),
                 'i_categories': obj.ignore_categories.all()} for obj in self.nakindcategorymap_set.all()],}
        rows = dict(
            (c, {'category': c, 'ontime': 0, 'expired': 0, 'total': 0}) for c in
            NACategory.objects.filter(id__in=cat_id))
        ignored_accidents = self.accidents(started=start_datetime, finished=finish_datetime, ignored=True)
        for a in self.accidents(started=start_datetime, finished=finish_datetime):
            rows[a.category]['total'] += 1
            result['total']['total'] += 1
            expired_dict = a.is_expired_by_region()
            duration_dict = a.accident_durations()
            duration = 0
            expired = False
            for r in self.regions.all():
                if r in expired_dict and expired_dict[r]:
                    expired = True
                    duration = duration_dict[r]
            if expired and a not in ignored_accidents:
                rows[a.category]['expired'] += 1
                result['total']['expired'] += 1
            else:
                rows[a.category]['ontime'] += 1
                result['total']['ontime'] += 1
            if not duration:
                duration = max([duration_dict[r] for r in self.regions.all() if r in duration_dict])
            result['accidents'].append({
                'instance': a,
                'duration': timedelta(minutes=duration).__str__()[:-3] if duration > 0 else u'',
                'is_expired': expired,
            })

        result['rows'] = rows.values()
        return result
