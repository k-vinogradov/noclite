from django.contrib import admin

from models import *


class NAKindCategoryMapAdmin(admin.StackedInline):
    model = NAKindCategoryMap
    filter_horizontal = ['kinds', 'categories']


@admin.register(NAAccident)
class NAAccidentAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_datetime'
    list_display = (
        'companies_list', 'cities_list', 'start_datetime', 'finish_datetime', 'category', 'kind', 'accident_durations')


@admin.register(NAConsolidationGroup)
class NAConsolidationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    filter_horizontal = ['regions']
    inlines = [NAKindCategoryMapAdmin]


@admin.register(NARegion)
class NARegionAdmin(admin.ModelAdmin):
    filter_horizontal = ['cities', ]


admin.site.register(NACompany)
admin.site.register(NACity)
admin.site.register(NACategory)
admin.site.register(NAKind)
admin.site.register(NADayType)
admin.site.register(NADay)
admin.site.register(NAWorkHours)
admin.site.register(NATimeLimit)
