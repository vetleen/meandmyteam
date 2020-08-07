from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

urlpatterns = i18n_patterns(
    path(_('admin/'), admin.site.urls),
    path(_('accounts/'), include('django.contrib.auth.urls')),

    path(_('dashboard/'), include('surveys.dashboard_urls')),
    path(_('surveys/'), include('surveys.surveys_urls')),
    path('', include('website.urls')),
    path(_('payments/'), include('payments.urls')),
    prefix_default_language=True

)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
