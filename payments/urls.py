from django.urls import path
from . import views


urlpatterns = [

    path('', views.current_plan_view, name='payments_current_plan'),
    path('set-up-payment-method/', views.set_up_payment_view, name='payments-set-up-payment-method'),
    path('set-up-payment-method-success/', views.set_up_payment_method_success, name='payments-set-up-payment-method-success'),
    path('set-up-payment-method-cancel/', views.set_up_payment_method_cancel, name='payments-set-up-payment-method-cancel'),
    path('use-payment-method/<payment_method_id>/', views.use_payment_method_view, name='payments-use-payment-method'),
    path('delete-payment-method/<payment_method_id>/', views.delete_payment_method_view, name='payments-delete-payment-method'),
    path('create-subscription/<subscription_id>/', views.create_subscription_view, name='payments-create-subscription'),
    path('cancel-subscription/<subscription_id>/', views.cancel_subscription_view, name='payments-cancel-subscription'),
    path('restart-cancelled-subscription/<subscription_id>/', views.restart_cancelled_subscription_view, name='payments-restart_cancelled-subscription'),
    path('change-plan/<price_id>/', views.change_subscription_price_view, name='payments-change-subscription-price'),

]
