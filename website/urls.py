from django.urls import path
from . import views

import os
from django.conf import settings

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


urlpatterns = [

    path('', views.index, name='index'),
    path('change-password/', views.change_password, name='change-password'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('login/', views.login_view, name='loginc'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-account/', views.edit_account_view, name='edit-account'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

]
