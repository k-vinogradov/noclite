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
    if accident.start_datetime:
        start_datetime = accident.start_datetime.astimezone(tz)
        start_date = start_datetime.strftime('%d.%m.%Y')
        start_time = start_datetime.strftime('%H<sup><u>%M</u></sup>')
    else:
        start_datetime = None
        start_date = ''
        start_time = ''

    if accident.finish_datetime:
        finish_datetime = accident.finish_datetime.astimezone(tz)
        finish_date = finish_datetime.strftime('%d.%m.%Y')
        finish_time = finish_datetime.strftime('%H<sup><u>%M</u></sup>')
    else:
        finish_datetime = None
        finish_date = ''
        finish_time = ''

    if not start_datetime and not finish_datetime:
        result_template = u'N/A'
    elif not start_datetime:
        result_template = u'<nobr>N/A &nbsp;&mdash;&nbsp;</nobr> <nobr>{finish_date} {finish_time}</nobr>'
    elif not finish_datetime:
        result_template = u'<nobr><strong>{start_date}</strong> {start_time} &mdash;</nobr> N/A'
    else:
        if start_datetime.date() == finish_datetime.date():
            result_template = u'<nobr><strong>{start_date}</strong></nobr>' \
                              u' <nobr>{start_time} &mdash; {finish_time}</nobr>'

        else:
            result_template = u'<nobr><strong>{start_date}</strong> {start_time} &mdash;</nobr>' \
                              u' <nobr><strong>{finish_date}</strong> {finish_time}</nobr>'
    result = result_template.format(
        start_date=start_date,
        finish_date=finish_date,
        start_time=start_time,
        finish_time=finish_time,
    )
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
            return '{0:.5}%'.format(value / arg * 100)
        except:
            pass
    return ''


@register.filter
def paragraphs(value):
    return mark_safe(u'<br/>'.join(value.split(u'\n')))