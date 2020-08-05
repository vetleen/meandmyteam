from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *
#from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

@admin.register(SurveySetting)
class SurveySettingAdmin(admin.ModelAdmin):
        list_display = ('organization', 'instrument', 'is_active', 'survey_interval', 'surveys_remain_open_days')


class DimensionInline(admin.StackedInline): #for use in UserAdmin
    model = Dimension
    can_delete = False



@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
        inlines = (DimensionInline, )

@admin.register(RatioScale)
class RatioScaleAdmin(admin.ModelAdmin):
        pass

@admin.register(Dimension)
class DimensionAdmin(admin.ModelAdmin):
        pass

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
        pass

class SurveyInstanceInline(admin.StackedInline): #for use in UserAdmin
    model = SurveyInstance
    can_delete = False

class RatioScaleDimensionResultInline(admin.StackedInline): #for use in UserAdmin
    model = RatioScaleDimensionResult
    can_delete = False

class RatioSurveyItemInline(admin.StackedInline): #for use in UserAdmin
    model = RatioSurveyItem
    can_delete = False

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
        inlines = (RatioScaleDimensionResultInline, RatioSurveyItemInline, SurveyInstanceInline)

@admin.register(Respondent)
class Respondent(admin.ModelAdmin):
        inlines = (SurveyInstanceInline, )

@admin.register(RespondentEmail)
class RespondentEmail(admin.ModelAdmin):
        pass
