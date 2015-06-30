# -*- coding: utf-8 -*-

from django.db import models


class NamedModel(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=u'Name')

    class Meta:
        abstract = True
        ordering = ['name', ]
        verbose_name = u'Element'

    def __unicode__(self):
        if self.id:
            return self.name
        else:
            return u'New {0}'.format(self.Meta.verbose_name.title())


class DeleteThroughIsActive(models.Model):
    is_active = models.BooleanField(default=True, blank=True, verbose_name=u'Active')

    class Meta:
        abstract = True

    def delete(self, using=None):
        self.is_active = False
        self.save()


class NACompany(NamedModel, DeleteThroughIsActive):
    class Meta(NamedModel.Meta):
        verbose_name = u'company'
        verbose_name_plural = u'companies'


class NACity(NamedModel, DeleteThroughIsActive):
    class Meta(NamedModel.Meta):
        verbose_name = u'city'
        verbose_name_plural = u'cities'


class NARegion(NamedModel, DeleteThroughIsActive):
    cities = models.ManyToManyField('NACity', verbose_name=u'Cities')

    class Meta(NamedModel):
        verbose_name = u'region'
        verbose_name_plural = u'regions'


class NACategory(DeleteThroughIsActive):
    number = models.IntegerField(unique=True, verbose_name=u'Number')
    title = models.CharField(max_length=4, verbose_name=u'Caption')
    description = models.TextField(blank=True, verbose_name=u'Description')

    class Meta(NamedModel.Meta):
        ordering = ['number', ]
        verbose_name = u'category'
        verbose_name_plural = u'categories'

    def __unicode__(self):
        return self.title if self.id else u'New Category'


class NAKind(DeleteThroughIsActive):
    code = models.CharField(max_length=8, unique=True, verbose_name=u'Code')
    title = models.CharField(max_length=255, verbose_name=u'Title')
    description = models.TextField(blank=True, verbose_name=u'Description')

    class Meta:
        ordering = ['code', 'title', ]
        verbose_name = u'kind of accident'
        verbose_name_plural = u'kinds of accident'

    def __unicode__(self):
        return u'{0}. {1}'.format(self.code, self.title) if self.id else u'New Kind of Accident'


class NAAccident(models.Model):
    company = models.ManyToManyField('NACompany', null=True, blank=True, verbose_name=u'Company')
    city = models.ManyToManyField('NACity', null=True, blank=True, verbose_name=u'City')
    start_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'Time of the beginning')
    finish_datetime = models.DateTimeField(blank=True, null=True, verbose_name=u'Time of the finishing')
    category = models.ForeignKey('NACategory', blank=True, null=True, verbose_name=u'Category')
    kind = models.ForeignKey('NAKind', blank=True, null=True, verbose_name=u'Kind')
    locations = models.TextField(blank=True, null=True, verbose_name=u'Locations')
    affected_customers = models.IntegerField(blank=True, null=True, verbose_name=u'Number of affected customers')
    magistral_customers_affected = models.BooleanField(blank=True, default=False, name=u'Magistral customers affected')
    reason = models.TextField(blank=True, null=True, verbose_name=u'Cause of accident')
    actions = models.TextField(blank=True, null=True, verbose_name=u'Emergency actions')
    iss_id = models.IntegerField(blank=True, null=True, verbose_name=u'ISS emergency job\'s number')

    class Meta:
        ordering = ['start_datetime', 'finish_datetime', ]
        verbose_name = u'accident'
        verbose_name_plural = u'accidents'

    def __unicode__(self):
        if self.id:
            return u'Accident #{0} (ISS-{1})'.format(self.id, self.iss_id) if self.iss_id else u'Accident #{0}'.format(
                self.id)
        else:
            return u'New Accident'

    def companies_list(self):
        return ', '.join([item.name for item in self.company.all()])

    def cities_list(self):
        return ', '.join([item.name for item in self.city.all()])

    def is_completed(self):
        if not (self.company and self.city and self.category and self.kind):
            return False
        elif not (self.start_datetime and self.finish_datetime and self.locations and self.affected_customers):
            return False
        elif not (self.reason and self.actions and self.iss_id):
            return False
        else:
            return True


class NADayType(NamedModel):
    start = models.TimeField(verbose_name=u'Start', null=True, blank=True)
    finish = models.TimeField(verbose_name=u'Finish', null=True, blank=True)
    default_workday = models.BooleanField(blank=True, default=False, verbose_name=u'Default workday')
    default_day_off = models.BooleanField(blank=True, default=False, verbose_name=u'Default day off')
    region = models.ForeignKey('NARegion', null=True, blank=True, verbose_name=u'Region')

    class Meta(NamedModel.Meta):
        verbose_name = u'type of day'
        verbose_name_plural = u'types of day'


class NADay(models.Model):
    date = models.DateField(verbose_name=u'Date')
    day_type = models.ForeignKey('NADayType', verbose_name=u'Type of day')

    class Meta:
        ordering = ['date', ]
        verbose_name = u'day'
        verbose_name_plural = u'days'

    def __unicode__(self):
        return self.date if self.id else u'New Day'


class NAWorkHours(models.Model):
    SCHEDULES = (
        ('WH', u'During the working hours'),
        ('24', u'Around the Clock')
    )

    category = models.ForeignKey('NACategory', verbose_name=u'Category of accident')
    kind = models.ForeignKey('NAKind', verbose_name=u'Kind of accident')
    main_schedule = models.CharField(max_length=4, choices=SCHEDULES, verbose_name=u'Schedule')
    magistral_affected_schedule = models.CharField(max_length=4, choices=SCHEDULES,
                                                   verbose_name=u'Schedule if magistral customers was affected')

    class Meta:
        ordering = ['kind', 'category', ]
        verbose_name = u'schedule'
        verbose_name_plural = u'schedules'

    def __unicode__(self):
        return u'{0} ({1})'.format(self.kind, self.category) if self.id else u'New schedule'


class NATimeLimits(models.Model):
    category = models.ForeignKey('NACategory', verbose_name=u'Category of accident')
    kind = models.ForeignKey('NAKind', verbose_name=u'Kind of accident')
    main_limit = models.IntegerField(verbose_name=u'Time limit (min)')
    magistral_affected_limit = models.IntegerField(verbose_name=u'Schedule if magistral customers was affected (min)')

    class Meta:
        ordering = ['category', 'kind', ]
        verbose_name = u'time limit'
        verbose_name_plural = u'time limits'

    def __unicode__(self):
        return u'{0} ({1})'.format(self.kind, self.category) if self.id else u'New Time Limit'