from django.urls import path
from . import views

import os
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [

    path('', views.index, name='index'),

    path(_('change-password/'), views.change_password, name='change-password'),
    path(_('sign-up/'), views.sign_up, name='sign-up'),
    path(_('login/'), views.login_view, name='loginc'),
    path(_('logout/'), views.logout_view, name='logout'),
    path(_('edit-account/'), views.edit_account_view, name='edit-account'),
    path(_('password-reset-request/'), views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path(_('password-reset-request-received/'), views.PasswordResetRequestReceivedView.as_view(), name='password-reset-request-received'),
    path(_('password-reset/<uidb64>/<token>/'), views.PasswordResetView.as_view(), name='password-reset'),
    path(_('password-reset-complete/'), views.password_reset_complete_view, name='password-reset-complete'),

    path(_('privacy-policy/'), views.privacy_policy_view, name='privacy-policy'),
    path(_('terms-and-conditions/'), views.terms_view, name='terms-and-conditions'),

    #REDIRECTED PERMANENTLY
    path(_('your-plan/'), RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path(_('choose-plan/'), RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path(_('change-plan/'), RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path(_('cancel-plan/'), RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
    path(_('show-interest-in-unavailable-plan/'), RedirectView.as_view(url=reverse_lazy('payments_current_plan'), permanent=True)),
]
