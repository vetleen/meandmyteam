from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

import os
from django.conf import settings

urlpatterns = [

        path('', views.dashboard_view, name='surveys-dashboard'),
        #path('edit-organization/', views.edit_organization_view, name='surveys-edit-organization'),
        path(_('add-or-remove-employees/'), views.add_or_remove_employee_view, name='surveys-add-or-remove-employees'),
        path(_('edit-employee/<uidb64>/'), views.edit_employee_view, name='surveys-edit-employee'),
        path(_('delete-employee/<uidb64>/'), views.delete_employee_view, name='surveys-delete-employee'),


]
