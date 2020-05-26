from django.urls import path
from . import views

urlpatterns = [

    path('', views.resources, name='index'),
    #path('privacy-policy/', views.privacy_policy_view, name='privacy-policy'),


]
