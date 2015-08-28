from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from www.constatnts import *


class Profile(models.Model):
    user = models.OneToOneField(User)
    comment = models.TextField(verbose_name=u'Comment', blank=True)

    def __unicode__(self):
        return u'{0} User Profile'.format(self.user.get_full_name())

    def get_short_name(self):
        if self.user.first_name and self.user.last_name:
            return u'{0}.{1}'.format(self.user.first_name[0].upper(), self.user.last_name.title())
        if self.user.last_name:
            return self.user.last_name.title()
        if self.user.first_name:
            return self.user.first_name.title()
        else:
            return self.user.username


class JournalManager(models.Manager):
    def create(self, level, message, objects):
        obj_list = ['{0}.{1}#{2}'.format(instance.__class__.__module__, instance.__class__.__name__, instance.pk) for
                    instance in objects]
        return super(JournalManager, self).create(related_objects=','.join(obj_list), level=level, message=message)

    def by_objects(self, *args):
        qs = self.all()
        for instance in args:
            s = '{0}.{1}#{2}'.format(instance.__class__.__module__, instance.__class__.__name__, instance.pk)
            qs = qs.filter(Q(related_objects__startswith=s + ',') | Q(related_objects__endswith=',' + s) | Q(
                related_objects__contains=',{0},'.format(s)) | Q(related_objects__exact=s))
        return qs


class Journal(models.Model):
    LEVELS = (
        (JL_CRITICAL, u'Critical'),
        (JL_ERROR, u'Error', ),
        (JL_WARNING, u'Warning'),
        (JL_NOTICE, u'Notice'),
        (JL_INFO, u'Informational', ),
        (JL_DEBUG, u'Debug',)
    )
    related_objects = models.TextField(verbose_name=u'related objects', blank=True)
    level = models.CharField(max_length=16, verbose_name=u'level', choices=LEVELS)
    date_time = models.DateTimeField(verbose_name=u'date and time', auto_now_add=True)
    message = models.TextField(verbose_name=u'messages')

    objects = JournalManager()

    class Meta:
        ordering = ['date_time']
        verbose_name = u'journal record'
        verbose_name_plural = u'journal records'

    def __str__(self):
        return 'Journal record #{0}-{1}'.format(self.id, self.date_time) if self.id else 'New Journal Record'

    __repr__ = __str__

    def __unicode__(self):
        return unicode(self.__str__())

    def get_related_objects(self):
        def local_import(class_name):
            mod = __import__(class_name)
            components = class_name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            return mod

        result = []
        for obj_string in self.related_objects.split(','):
            cls_name, obj_id = obj_string.split('#')
            result.append(local_import(cls_name).objects.get(pk=int(obj_id)))
        return result

    def get_related_objects_count(self):
        return len(self.related_objects.split(','))

    def remove_related_object(self, instance):
        obj_string = '{0}.{1}#{2}'.format(instance.__class__.__module__, instance.__class__.__name__, instance.pk)
        obj_list = [o for o in self.related_objects.split(',') if o != obj_string]
        self.related_objects = ','.join(obj_list)
        self.save()

    def save(self, *args, **kwargs):
        super(Journal, self).save(*args, **kwargs)
        if self.get_related_objects_count() == 0:
            self.delete()


class InformationSystem(models.Model):
    caption = models.CharField(max_length=255, verbose_name=u'System\' caption')
    url = models.CharField(max_length=255, verbose_name=u'URL')
    description = models.TextField(blank=True, null=True, verbose_name=u'Description')

    class Meta:
        verbose_name = u'system'
        ordering = ['caption', ]