from django.contrib import admin
from Company.models import (Transporteurs, Voyageurs, 
                            Asso_trans_voyageur, Voyages,
                            Compagnie, Transports)
# Register your models here.
class AdminTransporteurs(admin.ModelAdmin) :
    list_display = ("nom", 
    "prenom",
    "date_de_naissance",
    "adresse",
    "ville",
    "permis",
    "phone",
    "email" )

class AdminVoyageurs(admin.ModelAdmin) :
    list_display = ("nom_V",
    "prenom_V",
    "email")

class AdminAsso_trans_voyageur(admin.ModelAdmin) :
    list_display = ("voyageurs",  "transporteurs")

class AdminVoyages(admin.ModelAdmin) :
    list_display = ("date_depart",
    "date_arrivee", 
    "ville_depart",
    "ville_arrivee",
    "prix_unitaire",
    "transporteurs")

class AdminCompagnie(admin.ModelAdmin) :
    list_display = ("nom_E",
    "siren",
    "transporteurs")
class AdminTransports(admin.ModelAdmin) :
    list_display = ("marque",
    "matricule",
    "nombre_de_place",
    "voyages",
    "compagnie")


admin.site.register(Transporteurs, AdminTransporteurs)
admin.site.register(Voyageurs, AdminVoyageurs)
admin.site.register(Asso_trans_voyageur, AdminAsso_trans_voyageur)
admin.site.register(Voyages, AdminVoyages)
admin.site.register(Compagnie, AdminCompagnie)
admin.site.register(Transports, AdminTransports)