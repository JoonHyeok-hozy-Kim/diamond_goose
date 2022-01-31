"""diamond_goose URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accountapp.views import temp_welcome_view

urlpatterns = [
    path('', temp_welcome_view, name='home'),

    path('admin/', admin.site.urls),
    path('accounts/', include('accountapp.urls')),
    path('masterinfo/', include('masterinfoapp.urls')),
    path('dashboard/', include('dashboardapp.urls')),
    path('portfolio/', include('portfolioapp.urls')),
    path('assets/', include('assetapp.urls')),
    path('pensions/', include('pensionapp.urls')),
    path('exchange/', include('exchangeapp.urls')),
    path('hozylab/', include('hozylabapp.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
