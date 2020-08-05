from modeltranslation.translator import register, TranslationOptions
from .models import Scale, RatioScale, Instrument, Dimension, Item, SurveyItem, RatioSurveyItem

@register(Instrument)
class InstrumentTranslationOptions(TranslationOptions):
    fields = ('name', 'slug_name', 'description')

@register(Scale)
class ScaleTranslationOptions(TranslationOptions):
    fields = ('instruction',)

@register(RatioScale)
class RatioScaleTranslationOptions(TranslationOptions):
    fields = ('min_value_description', 'max_value_description')

@register(Dimension)
class DimensionTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Item)
class ItemTranslationOptions(TranslationOptions):
    fields = ('formulation', )

@register(SurveyItem)
class SurveyItemTranslationOptions(TranslationOptions):
    fields = ('item_formulation', )

@register(RatioSurveyItem)
class RatioSurveyItemTranslationOptions(TranslationOptions):
    pass