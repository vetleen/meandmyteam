from django.urls import path
from . import views

import os
from django.conf import settings

print ('OS says: %s'%(os.environ.get('CSRF_COOKIE_SECURE', "fuzzballs")))
print ('Django says: %s'%(settings.CSRF_COOKIE_SECURE))
print ('')
print ('OS says: %s'%(os.environ.get('SESSION_COOKIE_SECURE', "fuzzballs")))
print ('Django says: %s'%(settings.SESSION_COOKIE_SECURE))
print ('')
print ('OS says: %s'%(os.environ.get('X_FRAME_OPTIONS', "fuzzballs")))
print ('Django says: %s'%(settings.X_FRAME_OPTIONS))
print ('')
print ('OS says: %s'%(os.environ.get('SECURE_SSL_REDIRECT', "fuzzballs")))
print ('Django says: %s'%(settings.SECURE_SSL_REDIRECT))
print ('')
print ('OS says: %s'%(os.environ.get('SECURE_BROWSER_XSS_FILTER', "fuzzballs")))
print ('Django says: %s'%(settings.SECURE_BROWSER_XSS_FILTER))
print ('')
print ('OS says: %s'%(os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF', "fuzzballs")))
print ('Django says: %s'%(settings.SECURE_CONTENT_TYPE_NOSNIFF))
print ('')
#print ('OS says: %s'%(os.environ.get('SECURE_HSTS_SECONDS', "fuzzballs")))
#print ('Django says: %s'%(settings.SECURE_HSTS_SECONDS))
#print ('')

urlpatterns = [

    path('', views.index, name='index'),
    path('change-password/', views.change_password, name='change-password'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('login/', views.login_view, name='loginc'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-account/', views.edit_account_view, name='edit-account'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

]
