from django.contrib import admin

from models import *


class SimpleAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'is_active']
    list_filter = ['is_active', ]


class NAKindCategoryMapAdmin(admin.StackedInline):
    model = NAKindCategoryMap
    filter_horizontal = ['kinds', 'categories']


@admin.register(NAConsolidationGroup)
class NAConsolidationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    filter_horizontal = ['regions', 'companies']
    inlines = [NAKindCategoryMapAdmin]


@admin.register(NARegion)
class NARegionAdmin(SimpleAdmin):
    filter_horizontal = ['cities', ]
    list_display = ['__unicode__', 'cities_str', 'is_active', ]


@admin.register(NADay)
class NADayAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'day_type', 'region']


@admin.register(NAWorkHours)
class NAWorkHoursAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'category', 'kind', 'main_schedule', 'magistral_affected_schedule']


@admin.register(NADayType)
class NADayTypeAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'region', 'start', 'finish', 'default_settings']


@admin.register(NATimeLimit)
class NATimeLimit(admin.ModelAdmin):
    list_display = ['__unicode__', 'main_limit', 'magistral_affected_limit']


admin.site.register(NACompany, SimpleAdmin)
admin.site.register(NACity, SimpleAdmin)
admin.site.register(NACategory, SimpleAdmin)
admin.site.register(NAKind, SimpleAdmin)
