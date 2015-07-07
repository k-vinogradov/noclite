from django import forms
from django.core.management import settings
from pytz import all_timezones

class ListDateIntervalForm(forms.Form):
    started = forms.DateField()
    finished = forms.DateField()
    tz = forms.ChoiceField(choices=((t, t) for t in all_timezones), initial=settings.TIME_ZONE)