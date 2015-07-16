from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from www.models import Profile, Journal


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'


class UserAdminWithProfile(UserAdmin):
    inlines = (ProfileInline,)


class JournalAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'level', 'message')
    list_display_links = ('date_time',)


admin.site.unregister(User)
admin.site.register(User, UserAdminWithProfile)
admin.site.register(Journal, JournalAdmin)