from django.contrib import admin

#from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Product, Organization, Employee, Survey, Question, SurveyInstance


# Register your models here.
'''
class QuestionInline(admin.TabularInline): #for use in UserAdmin
    model = Question
    can_delete = False
    verbose_name_plural = 'questions'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
        list_display = ('name', 'short_description')
        inlines = (QuestionInline,)

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
        list_display = ('respondent', 'get_owner', 'get_url_token', 'survey', 'completed')
'''