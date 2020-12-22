"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from websiteBackbone import views

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'posts/', include('manageBlog.urls')),
    path(r'finance/', include('financeAnalysis.urls')),
    path(r'analysis/', include('simpleAnalysis.urls')),
    path(r'register/', views.register, name="register"),
    path(r'accounts/', include("django.contrib.auth.urls")),
    path(r'positions/', include('positions.urls')),
    path(r'', include('websiteBackbone.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
