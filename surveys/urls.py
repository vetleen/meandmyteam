from django.urls import path
from . import views

import os
from django.conf import settings

urlpatterns = [

        path('', views.dashboard_view, name='surveys-dashboard'),
        path('edit-organization/', views.edit_organization_view, name='surveys-edit-organization'),
        path('edit-coworker/', views.edit_coworker_view, name='surveys-edit-coworker'),
        path('delete-coworker/<uidb64>/', views.delete_coworker_view, name='surveys-delete-coworker'),
        path('edit-coworker/<uidb64>/', views.edit_individual_coworker_view, name='edit-individual-coworker'),
        path('set-up-employee-satisfaction-tracking/', views.set_up_employee_satisfaction_tracking, name='surveys-set-up-employee-satisfaction-tracking'),
        #path('answer-survey/<si_idb64>/', views.answer_survey_view, name='surveys-answer-survey'),
]
