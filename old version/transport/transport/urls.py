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

from django.urls import path, include
from Company.views import (home,infos_personnelles,finaliser_reservation, reservation,  homepage2, homepage3, about,vider_table_view, 
question, contact, comming_soon, career, generate_pdf, login_chauffeur,changer_mot_de_passe, dashboard_chauffeur,custom_404_view,
dashboard_chauffeur, user_login, verify_code, dashboard, tchat, import_excel_view, register_user, password_reset_voyageur, password_reset_chauffeur,
sign_in, sign_up, blog, blog_single, team, privacy, telecharger_passagers_pdf, payment_page, payment_complete, lancer_paiement)


from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    path('admin/import-excel/', import_excel_view, name='import_excel'),
    path("admin/vider-table/", vider_table_view, name="vider-table"),
    path('admin/', admin.site.urls), # Use the default admin site for the main admin interface


    path('', home, name='home'),

    path('page2/', homepage2, name='homepage2'),
    path('page3/', homepage3, name='homepage3'),
    path("infos/", infos_personnelles, name="infos_personnelles"),
    path("reservation/", reservation, name="reservation"),
    path("finaliser-reservation/", finaliser_reservation, name="finaliser_reservation"),
    path("pdf-recap/", generate_pdf, name="pdf_recap"),

    path("paiement/", payment_page, name="payment"),
    path("paiement/complete/", payment_complete, name="payment_complete"),
    path('lancer-paiement/', lancer_paiement, name='lancer_paiement'),

  
    path('mot-de-passe-voyageur/', password_reset_voyageur, name='password_reset_voyageur'),
    path('mot-de-passe-chauffeur/', password_reset_chauffeur, name='password_reset_chauffeur'),
    path("dashboard/pdf-passagers/", telecharger_passagers_pdf, name="telecharger_passagers_pdf"),

    path('login-user/', user_login, name='login_user'),
    path('dashboard/voyageur/', dashboard, name='dashboard'),
    path('changer-mot-de-passe/', changer_mot_de_passe, name='changer_mot_de_passe'),
    path('login-chauffeur/', login_chauffeur, name='login_chauffeur'),
    path('dashboard/chauffeur/', dashboard_chauffeur, name='dashboard_chauffeur'),

    path('login-user/', user_login, name='user_login'),
    path('verify/', verify_code, name='verify_code'),

    path('tchat/<int:transporteur_id>/', tchat, name='tchat'),

    path('register/', register_user, name='register_user'),

    path('about/', about, name='about'),
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

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'Company.views.custom_404_view'