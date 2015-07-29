from django import forms
from django.core.management import settings
from django.forms import ValidationError

TIME_ZONES = (
    (settings.TIME_ZONE, 'Default ({0})'.format(settings.TIME_ZONE)),
    ('Etc/GMT-3', 'Etc/GMT-3 (Moscow)'),
    ('Etc/GMT-7', 'Etc/GMT-7 (Krasnoyarsk)'),
)

class ListDateIntervalForm(forms.Form):
    started = forms.DateField()
    finished = forms.DateField()
    tz = forms.ChoiceField(choices=TIME_ZONES, initial=settings.TIME_ZONE)


class ConsolidationReportForm(forms.Form):
    start = forms.DateTimeField()
    finish = forms.DateTimeField()
    tz = forms.ChoiceField(choices=TIME_ZONES, initial=settings.TIME_ZONE)

    def clean(self):
        cleaned_data = super(ConsolidationReportForm, self).clean()
        if cleaned_data['start'] > cleaned_data['finish']:
            raise ValidationError('Date of the reports\'s begining must be earlier than end\'s date.')
        cleaned_data['start'] = cleaned_data['start'].replace(tzinfo=None)
        cleaned_data['finish'] = cleaned_data['finish'].replace(tzinfo=None)
        return cleaned_data