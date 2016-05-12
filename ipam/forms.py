from django import forms
from ipam.models import Vrf

from re import match


class FreeBlocks4ReportForm(forms.Form):
    vrf = forms.ModelChoiceField(queryset=Vrf.objects.all(), label=u'VRF Table')
    prefix = forms.CharField(max_length=18, label=u'Root Prefix')

    def clean_prefix(self):
        data = self.cleaned_data['prefix']
        if not match(r'(\d{1,3}\.){3}\d{1,3}/\d{1,2}', data.strip()):
            raise forms.ValidationError('Invalid IPv4-prefix')
        return data
