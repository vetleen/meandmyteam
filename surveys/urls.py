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


]
