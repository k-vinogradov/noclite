from django.contrib import admin
from models import (Prefix4, Vrf)
# Register your models here.

def status_display(obj):
    return obj.get_status_display()


status_display.short_description = 'Status'


class PrefixAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'vrf', 'parent', status_display)
    list_display_links = ('prefix',)


admin.site.register(Vrf)
admin.site.register(Prefix4, PrefixAdmin)