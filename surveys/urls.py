from django.urls import path
from . import views

import os
from django.conf import settings

urlpatterns = [

        path('', views.dashboard_view, name='surveys-dashboard'),
        path('create-organization/', views.create_organization_view, name='surveys-create-organization'),
        path('edit-coworker/', views.edit_coworker_view, name='surveys-edit-coworker'),
        path('delete-coworker/<uidb64>/', views.delete_coworker_view, name='surveys-delete-coworker'),


]
