from django.urls import path
from . import views

import os
from django.conf import settings

from django.urls import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [

    path('', views.index, name='index'),

    path('change-password/', views.change_password, name='change-password'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('login/', views.login_view, name='loginc'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-account/', views.edit_account_view, name='edit-account'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-request-received/', views.PasswordResetRequestReceivedView.as_view(), name='password-reset-request-received'),
    path('password-reset/<uidb64>/<token>/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-complete/', views.password_reset_complete_view, name='password-reset-complete'),

    path('privacy-policy/', views.privacy_policy_view, name='privacy-policy'),

    #REDIRECTED PERMANENTLY
    path('your-plan/', RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path('choose-plan/', RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path('change-plan/', RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path('cancel-plan/', RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path('show-interest-in-unavailable-plan/', RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),

]
