from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Organization, Event


#class SalesArgumentInline(admin.StackedInline): #for use in PlanAdmin
#    model = SalesArgument
#    can_delete = False
#    verbose_name_plural = 'sales arguments'

#admin.site.register(Plan)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
        list_display = ('category', 'user', 'comment', 'time')
        #inlines = (SalesArgumentInline,)

'''
@admin.register(SalesArgument)
class SalesArgumentAdmin(admin.ModelAdmin):
        list_display = ('argument', 'priority', 'badge_type','badge_text', 'is_active')
'''
class OrganizationInline(admin.StackedInline): #for use in UserAdmin
    model = Organization
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (OrganizationInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
