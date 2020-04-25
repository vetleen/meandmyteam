from django.urls import path
from . import views

import os
from django.conf import settings

'''
print ('Django running with the following settings...')
print ('CSRF_COOKIE_SECURE:')
print ('OS says: %s'%(os.environ.get('CSRF_COOKIE_SECURE', "Not set")))
print ('Django says: %s'%(settings.CSRF_COOKIE_SECURE))
print ('SESSION_COOKIE_SECURE:')
print ('OS says: %s'%(os.environ.get('SESSION_COOKIE_SECURE', "Not set")))
print ('Django says: %s'%(settings.SESSION_COOKIE_SECURE))
print ('X_FRAME_OPTIONS:')
print ('OS says: %s'%(os.environ.get('X_FRAME_OPTIONS', "Not set")))
print ('Django says: %s'%(settings.X_FRAME_OPTIONS))
print ('SECURE_SSL_REDIRECT:')
print ('OS says: %s'%(os.environ.get('SECURE_SSL_REDIRECT', "Not set")))
print ('Django says: %s'%(settings.SECURE_SSL_REDIRECT))
print ('SECURE_BROWSER_XSS_FILTER:')
print ('OS says: %s'%(os.environ.get('SECURE_BROWSER_XSS_FILTER', "Not set")))
print ('Django says: %s'%(settings.SECURE_BROWSER_XSS_FILTER))
print ('SECURE_CONTENT_TYPE_NOSNIFF:')
print ('OS says: %s'%(os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF', "Not set")))
print ('Django says: %s'%(settings.SECURE_CONTENT_TYPE_NOSNIFF))
'''

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


]
