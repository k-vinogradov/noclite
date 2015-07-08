from django.db import models
from django.shortcuts import redirect


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