from django.contrib import admin

from models import *

@admin.register(NAAccident)
class NAAccidentAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_datetime'
    list_display = ('companies_list', 'cities_list', 'start_datetime', 'finish_datetime', 'category', 'kind')

admin.site.register(NACompany)
admin.site.register(NACity)
admin.site.register(NACategory)
admin.site.register(NAKind)
admin.site.register(NADayType)
admin.site.register(NADay)
admin.site.register(NAWorkHours)
admin.site.register(NATimeLimits)
