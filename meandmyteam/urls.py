"""meandmyteam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    prefix_default_language=False

)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
