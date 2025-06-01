from django.contrib import admin
from Company.models import (Transporteurs, Voyageurs, 
                            Asso_trans_voyageur, Voyages,
                            Compagnie, Transports)
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExcelImportForm


from import_excel import FillData  # ton fichier existant

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

class AdminVoyages(admin.ModelAdmin) :
    list_display = ("date_depart",
    "date_arrivee", 
    "ville_depart",
    "ville_arrivee",
    "prix_unitaire",
    "transporteurs")

class AdminCompagnie(admin.ModelAdmin) :
    list_display = ("name",
    "siren",
    "transporteurs")
class AdminTransports(admin.ModelAdmin) :
    list_display = ("marque",
    "matricule",
    "nombre_de_place",
    "voyages",
    "compagnie")


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
admin.site.register(Asso_trans_voyageur, AdminAsso_trans_voyageur)
admin.site.register(Voyages, AdminVoyages)
admin.site.register(Compagnie, AdminCompagnie)
admin.site.register(Transports, AdminTransports)