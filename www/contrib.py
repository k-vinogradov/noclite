from django.db import models
from django.shortcuts import redirect
from django.utils.timezone import get_default_timezone
from www.constatnts import JL_INFO


class AddUserInstanceViewMixin(object):
    def form_valid(self, form):
        if 'pk' in self.kwargs or 'slug' in self.kwargs:
            instance = self.get_object()
            for key in form.cleaned_data:
                setattr(instance, key, form.cleaned_data[key])
            instance.save(user=self.request.user)
        else:
            instance = self.model(**form.cleaned_data)
            instance.save(user=self.request.user)
        return redirect(instance.get_absolute_url())


class AdditionalContextViewMixin(object):
    page_title = u''

    def get_context_data(self, **kwargs):
        context = super(AdditionalContextViewMixin, self).get_context_data(**kwargs)
        if len(self.page_title) > 0:
            context['page_title'] = self.page_title
        return context


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


class DeleteThroughIsActiveManager(models.Manager):
    def all(self, inactive=False):
        if inactive:
            return super(DeleteThroughIsActiveManager, self).all()
        else:
            return self.filter(is_active=True)


class ActiveAbleAcives(models.Manager):
    def get_queryset(self):
        return super(ActiveAbleAcives, self).get_queryset().filter(is_active=True)


class ActiveAble(models.Model):
    is_active = models.BooleanField(default=True, blank=True, verbose_name=u'Active')

    objects = DeleteThroughIsActiveManager()
    actives = ActiveAbleAcives()

    class Meta:
        abstract = True

    def delete(self, using=None):
        self.is_active = False
        self.save()

    @staticmethod
    def limit_choice():
        return {'is_active': True}


class JournalMixin(object):
    def write_to_journal(self, message, user=None, level=JL_INFO):
        from www.models import Journal
        if user:
            object_list = [self, user]
        else:
            object_list = [self]

        Journal.objects.create(level=JL_INFO, message=message, objects=object_list)

    def journal_changes(self, user=None, p_instance=None, api_request_id=None):
        """
        :type self: models.Model
        :param user:
        :type user: django.contrib.auth.models.User
        :param p_instance:
        :type p_instance: models.Model
        :param api_request_id:
        """
        model_class = self.__class__
        meta = model_class._meta
        if p_instance:
            if user:
                message = u'User {full_name} ({email}) updated {verbose_name}.'.format(
                    full_name=' '.join((user.first_name, user.last_name)),
                    email=user.email,
                    verbose_name=meta.verbose_name)
            else:
                message = u"{verbose_name} update by API request {req_id}".format(
                    verbose_name=meta.verbose_name.upper(),
                    req_id=api_request_id)
            for field in meta.fields:
                value = getattr(self, field.name)
                p_value = getattr(p_instance, field.name)
                verbose_name = field._verbose_name
                if value and field.__class__.__name__ == 'DateTimeField':
                    value = unicode(value.astimezone(get_default_timezone()))
                elif value:
                    value = unicode(value)
                else:
                    value = None
                if p_value and field.__class__.__name__ == 'DateTimeField':
                    p_value = unicode(p_value.astimezone(get_default_timezone()))
                elif value:
                    p_value = unicode(p_value)
                else:
                    p_value = None
                if value != p_value:
                    message += u'\n{0}: {1}'.format(verbose_name, value if value else u'N/A')

            for field in meta._many_to_many():
                if getattr(self, field.name).count() > 1:
                    verbose_name = field._verbose_name
                    new_list = getattr(self, field.name).all()
                    old_list = getattr(p_instance, field.name).all()
                    added = [unicode(item) for item in new_list if item not in old_list]
                    removed = [unicode(item) for item in old_list if item not in new_list]
                    if len(added) > 0:
                        message += u'\n{0} (added): {1}'.format(verbose_name, u','.join(added))
                    if len(added) > 0:
                        message += u'\n{0} (removed): {1}'.format(verbose_name, u','.join(removed))
        else:
            if user:
                message = u'User {full_name} ({email}) added new {verbose_name}.'.format(
                    full_name=' '.join((user.first_name, user.last_name)),
                    email=user.email,
                    verbose_name=meta.verbose_name)
            else:
                message = u'New {verbose_name} created by API request ID {req_id}'.format(
                    verbose_name=meta.verbose_name.upper(),
                    req_id=api_request_id)
            for field in meta.fields:
                if getattr(self, field.name):
                    verbose_name = field._verbose_name
                    value = unicode(getattr(self, field.name))
                    message += u'\n{0}: {1}'.format(verbose_name, value)
            for field in meta._many_to_many():
                if getattr(self, field.name).count() > 1:
                    verbose_name = field._verbose_name
                    value = ', '.join([unicode(v) for v in getattr(self, field.name).all()])
                    message += u'\n{0}: {1}'.format(verbose_name, value)
        self.write_to_journal(message, user)


class JournalViewMixin(object):
    def form_valid(self, form):
        if 'pk' in self.kwargs or 'slug' in self.kwargs:
            p_instance = self.get_object()
        else:
            p_instance = None
        instance = form.save()
        instance.journal_changes(self.request.user, p_instance=p_instance)
        return redirect(self.get_success_url() if self.success_url else instance.get_absolute_url())
