from django.urls import path
from . import views

import os
from django.conf import settings

urlpatterns = [

        path('setup-tracking/<instrument>/', views.setup_instrument_view, name='surveys-setup-instrument'),
        path('survey-details/<uidb64>/<instrument>/', views.survey_details_view, name='surveys-survey-details'),
        path('answer/<token>/', views.answer_survey_view, name='surveys-answer-survey'),
        path('answer/<token>/<page>/', views.answer_survey_view, name='surveys-answer-survey-pages'),

]
