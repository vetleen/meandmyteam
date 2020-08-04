from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

import os
from django.conf import settings

urlpatterns = [

        path(_('setup-tracking/<instrument>/'), views.setup_instrument_view, name='surveys-setup-instrument'),
        path(_('survey-details/<uidb64>/<instrument>/'), views.survey_details_view, name='surveys-survey-details'),
        path(_('answer/<token>/'), views.answer_survey_view, name='surveys-answer-survey'),
        path(_('answer/<token>/<page>/'), views.answer_survey_view, name='surveys-answer-survey-pages'),

]
