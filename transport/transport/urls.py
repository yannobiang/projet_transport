"""transport URL Configuration

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
from django.contrib import admin
from django.urls import path
from Company.views import (home, homepage2, homepage3, about,
indisponible, question, contact, comming_soon, career,
sign_in, sign_up, blog, blog_single, team, privacy)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('page2/', homepage2, name='homepage2'),
    path('page3/', homepage3, name='homepage3'),
    path('about/', about, name='about'),
    path('Erreur 404/', indisponible, name='indisponible'),
    path('FAQ/', question, name='question'),
    path('contact/', contact, name='contact'),
    path('comming soon/', comming_soon, name='comming_soon'),
    path('carrière/', career, name = 'career'),
    path('login/', sign_in, name = 'sign_in'),
    path('logout/', sign_up, name = 'sign_up'),
    path('blog/', blog, name = 'blog'),
    path('blog-single/', blog_single, name='blog_single'),
    path('team/', team, name='team'),
    path('privacy-policy/', privacy, name='privacy'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
