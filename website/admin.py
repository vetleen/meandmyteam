from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Subscriber


#class SalesArgumentInline(admin.StackedInline): #for use in PlanAdmin
#    model = SalesArgument
#    can_delete = False
#    verbose_name_plural = 'sales arguments'

#admin.site.register(Plan)
'''
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
        list_display = ('name', 'description', 'monthly_price', 'yearly_price')
        #inlines = (SalesArgumentInline,)
'''
'''
@admin.register(SalesArgument)
class SalesArgumentAdmin(admin.ModelAdmin):
        list_display = ('argument', 'priority', 'badge_type','badge_text', 'is_active')
'''
class SubscriberInline(admin.StackedInline): #for use in UserAdmin
    model = Subscriber
    can_delete = False
    #verbose_name_plural = 'subscribers'

class UserAdmin(BaseUserAdmin):
    inlines = (SubscriberInline,)
# Re-register UserAdmin

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
