from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter(name='addcss')
def add_css(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def form_filed_type(field):
    return type(field).__name__


@register.filter
def accident_time_interval(accident, tz):
    if not accident.start_datetime and accident.finish_datetime:
        result = u'N/A'
    elif not accident.start_datetime:
        finish_datetime = accident.finish_datetime.astimezone(tz)
        result = u'<nobr>N/A &nbsp;&mdash;&nbsp;</nobr> <nobr>{0}</nobr>'.format(
            finish_datetime.strftime('<strong>%d.%m.%Y</strong> %H<sup><u>%M</u></sup>'))
    elif not accident.finish_datetime:
        start_datetime = accident.start_datetime.astimezone(tz)
        result = u'<nobr>{0} &nbsp;&mdash;&nbsp;</nobr> N/A'.format(
            start_datetime.strftime('<strong>%d.%m.%Y</strong> %H<sup><u>%M</u></sup>'))
    else:
        start_datetime = accident.start_datetime.astimezone(tz)
        finish_datetime = accident.finish_datetime.astimezone(tz)
        if start_datetime.date() == finish_datetime.date():
            result = u'<nobr>{0} &nbsp;&mdash;&nbsp;</nobr> <nobr>{1}</nobr>'.format(
                start_datetime.strftime('<strong>%d.%m.%Y</strong> %H<sup><u>%M</u></sup>'),
                finish_datetime.strftime('%H<sup><u>%M</u></sup>'))
        else:
            result = u'<nobr>{0} &nbsp;&mdash;&nbsp;</nobr> <nobr>{1}</nobr>'.format(
                start_datetime.strftime('<strong>%d.%m.%Y</strong> %H<sup><u>%M</u></sup>'),
                finish_datetime.strftime('<strong>%d.%m.%Y</strong> %H<sup><u>%M</u></sup>'))
    return mark_safe(result)


@register.filter
def html_datetime_format(dt, tz):
    return mark_safe(dt.astimezone(tz).strftime(u'%d.%m.%Y %H<sup><u>%M</u></sup>') if dt else u'')


@register.filter
def iss_job_url(id):
    from django.conf import settings

    return settings.ISS_JOB_URL_TEMPLATE.format(id=id)


@register.filter
def divide(value, arg):
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            return value / arg
    except:
        pass
    return ''


@register.filter
def percent(value, arg=None):
    if arg:
        try:
            value = float(value)
            arg = float(arg)
            return '{0:.5}%'.format(value/arg*100)
        except:
            pass
    return ''

@register.filter
def paragraphs(value):
    return mark_safe(u'<br/>'.join(value.split(u'\n')))