from django.urls import path
from . import views

import os
from django.conf import settings


urlpatterns = [

    path('', views.index, name='index'),
    path('change-password/', views.change_password, name='change-password'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('login/', views.login_view, name='loginc'),
    path('logout/', views.logout_view, name='logout'),


    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-request-received/', views.PasswordResetRequestReceivedView.as_view(), name='password-reset-request-received'),
    path('password-reset/<uidb64>/<token>/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-complete/', views.password_reset_complete_view, name='password-reset-complete'),

    path('edit-account/', views.edit_account_view, name='edit-account'),
    path('your-plan/', views.your_plan_view, name='your-plan'),
    path('choose-plan/', views.choose_plan_view, name='choose-plan'),
    path('change-plan/', views.change_plan_view, name='change-plan'),
    path('cancel-plan/', views.cancel_plan_view, name='cancel-plan'),
    path('show-interest-in-unavailable-plan/', views.show_interest_in_unavailable_plan, name='show-interest-in-unavailable-plan'),
    path('set-up-subscription/', views.set_up_subscription, name='set-up-subscription'),
    path('set-up-subscription-success/', views.set_up_subscription_success, name='set-up-subscription-success'),
    path('set-up-subscription-cancel/', views.set_up_subscription_cancel, name='set-up-subscription-cancel'),

    path('privacy-policy/', views.privacy_policy_view, name='privacy-policy'),


]
