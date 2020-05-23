from django.contrib import admin

#from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Product, Organization, Employee, Survey, Question, SurveyInstance
from website.admin import UserAdmin as BaseUserAdmin, SubscriberInline


# Register your models here.

class QuestionInline(admin.TabularInline): #for use in UserAdmin
    model = Question
    can_delete = False
    verbose_name_plural = 'questions'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
        list_display = ('name', 'short_description')
        inlines = (QuestionInline,)

class OrganizationInline(admin.StackedInline): #for use in UserAdmin
    model = Organization
    can_delete = False
    verbose_name_plural = 'organization' #these should never be plural

class UserAdmin(BaseUserAdmin):
    inlines = (OrganizationInline, SubscriberInline)

class EmployeeInline(admin.TabularInline): #for use in UserAdmin
    model = Employee
    can_delete = False
    verbose_name_plural = 'employees'

class SurveyInline(admin.TabularInline): #for use in UserAdmin
    model = Survey
    can_delete = False
    verbose_name_plural = 'surveys'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address_line_1', 'address_line_2', 'zip_code', 'city', 'country')
    inlines = (EmployeeInline, SurveyInline)

@admin.register(SurveyInstance)
class SurveyInstanceAdmin(admin.ModelAdmin):
        list_display = ('respondent', 'survey', 'get_url_token', 'completed')



#reregister
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
