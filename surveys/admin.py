from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *
#from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

@admin.register(SurveySetting)
class SurveySettingAdmin(admin.ModelAdmin):
        list_display = ('organization', 'instrument', 'is_active', 'survey_interval', 'surveys_remain_open_days')

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
        pass
