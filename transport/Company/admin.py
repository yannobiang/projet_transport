from django.contrib import admin
from Company.models import (Transporteurs, Voyageurs, CustomUser,
                            Asso_trans_voyageur, Voyages,
                            Compagnie, Transports, HistoriqueImport)
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExcelImportForm
from .forms import ViderTableForm
from django.apps import apps
from import_excel import FillData  # ton fichier existant




@admin.register(HistoriqueImport)
class HistoriqueImportAdmin(admin.ModelAdmin):
    list_display = ("fichier", "utilisateur", "date_import")
    list_filter = ("utilisateur", "date_import")
    search_fields = ("fichier",)
# Remplacer tous les enregistrements admin

class AdminTransports(admin.ModelAdmin):
    list_display = (
        "marque",
        "matricule",
        "nombre_de_place",
        "compagnie",
        "get_voyages"
    )

    def get_voyages(self, obj):
        return ", ".join([str(v) for v in obj.voyages_set.all()])

# Register your models here.
class AdminTransporteurs(admin.ModelAdmin) :
    list_display = ("name", 
    "firstname",
    "date_de_naissance",
    "adresse",
    "ville",
    "permis",
    "phone",
    "email" )

class AdminVoyageurs(admin.ModelAdmin) :
    list_display = ("name",
    "firstname",
    "email")

class AdminAsso_trans_voyageur(admin.ModelAdmin) :
    list_display = ("voyageurs",  "transporteurs")

class AdminVoyages(admin.ModelAdmin):
    list_display = (
        "date_depart",
        "date_arrivee", 
        "ville_depart",
        "ville_arrivee",
        "prix_unitaire",
        "get_transports_lies"
    )

    def get_transports_lies(self, obj):
        return ", ".join([f"{t.marque} ({t.matricule})" for t in obj.transports.all()])
    get_transports_lies.short_description = "Transports liés"

class AdminCompagnie(admin.ModelAdmin):
    list_display = ("name", "siren", "get_transporteurs")

    def get_transporteurs(self, obj):
        return ", ".join([
            f"{t.name} {t.firstname}"
            for t in Transporteurs.objects.filter(compagnie=obj)
        ])
    get_transporteurs.short_description = "Transporteurs associés"

class AdminVoyages(admin.ModelAdmin):
    list_display = (
        "date_depart", "date_arrivee", "ville_depart",
        "ville_arrivee", "prix_unitaire", "get_transports"
    )

    def get_transports(self, obj):
        return ", ".join([
            f"{t.marque} ({t.matricule})"
            for t in Transports.objects.filter(voyages=obj)
        ])
    get_transports.short_description = "Transports liés"


class CustomImportAdmin(admin.ModelAdmin):
    change_list_template = "admin/excel_import.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-excel/", self.admin_site.admin_view(self.import_excel))
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES["excel_file"]
                with open("temp_import.xlsx", "wb+") as destination:
                    for chunk in excel_file.chunks():
                        destination.write(chunk)

                FillData("temp_import.xlsx").charge()
                messages.success(request, "✅ Importation réussie.")
                return redirect("..")
        else:
            form = ExcelImportForm()

        context = {
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/excel_import.html", context)
 

admin.site.register(Transporteurs, CustomImportAdmin)
admin.site.register(Voyageurs, AdminVoyageurs)
admin.site.register(Transports, AdminTransports)
admin.site.register(Asso_trans_voyageur, AdminAsso_trans_voyageur)
admin.site.register(Voyages, AdminVoyages)
admin.site.register(Compagnie, AdminCompagnie)
