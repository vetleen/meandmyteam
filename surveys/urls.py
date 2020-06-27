from django.urls import path
from . import views

import os
from django.conf import settings

urlpatterns = [

        path('', views.dashboard_view, name='surveys-dashboard'),
        #path('edit-organization/', views.edit_organization_view, name='surveys-edit-organization'),
        path('add-or-remove-employees/', views.add_or_remove_employee_view, name='surveys-add-or-remove-employees'),
        path('edit-employee/<uidb64>/', views.edit_employee_view, name='surveys-edit-employee'),
        path('delete-employee/<uidb64>/', views.delete_employee_view, name='surveys-delete-employee'),

        path('setup-tracking/<instrument>/', views.setup_instrument_view, name='surveys-setup-instrument'),
        #path('co-worker-satisfaction/<date_close>/', views.co_worker_satisfaction_data_view, name='surveys-co-worker-satisfaction-data'),

]
