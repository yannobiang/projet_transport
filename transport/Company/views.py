from django.shortcuts import render, HttpResponse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from datetime import date, datetime, timedelta, time, timezone
from django.utils.timezone import now, localdate, make_aware
from django.contrib.admin.views.decorators import staff_member_required
from django.apps import apps
from .forms import ViderTableForm
from openpyxl import load_workbook
from .models import (Voyages,MessageClientChauffeur, CustomUser, VerificationCode, 
                     Voyageurs, Transporteurs, Reservation, Asso_trans_voyageur, 
                     Transports, HistoriqueImport)
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
logger = logging.getLogger(__name__)
from .utils import convert, get_weekday, get_month, safe_format_iso, payer, verifier_paiement
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import get_template
from xhtml2pdf import pisa
from itertools import zip_longest
import json
from django.db.models import Exists, OuterRef
from django.core.files import File
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from import_excel import FillData
from .forms import ExcelImportForm
import os
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse
from reportlab.pdfgen import canvas
import io
from io import BytesIO
import paypalrestsdk
from django.http import JsonResponse





# Create your views here.
User = get_user_model()

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" ou "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET_KEY
})

def home(request):

    """cette fonction lance la page home du site
        le result est une liste qui content autant de dictionnaire que de voyage
        chaque dictionnaire contient les informations sur le voyage
    """
    current = date.today().strftime("%Y-%m-%d")

    if request.method == 'POST':
        dataSend = dict(request.POST)
        # Supposons que `today` soit un `date` :

        # Convertir en datetime à minuit, puis rendre aware
        today = datetime.strptime(dataSend['date_depart'][0], "%Y-%m-%d").date()


        # Pour yesterday et tomorrow, même logique :
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        try:
            date_retour = datetime.strptime(dataSend['date_depart'][0], "%Y-%m-%d").date()
            # datetime.strptime(dataSend['date_retour'][0], "%Y-%m-%d").date()
        except:
            date_retour = None


        list_of_depart = [col.title() for col in dataSend['depart']]
        list_of_destination = [col.title() for col in dataSend['destination']]


        if dataSend['trip'][0] == "aller":
            
            result_hier = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=yesterday,
                ville_depart__in=list_of_depart,
                ville_arrivee__in=list_of_destination
            ).order_by('date_depart').values(
                "ville_depart", "ville_arrivee", "date_depart", "date_arrivee", "prix_unitaire", "id"
            ))

            result = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=today,
                ville_depart__in=list_of_depart,
                ville_arrivee__in=list_of_destination
            ).order_by('date_depart').values(
                "ville_depart", "ville_arrivee", "date_depart", "date_arrivee", "prix_unitaire", "id"
            ))

            result_demain = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=tomorrow,
                ville_depart__in=list_of_depart,
                ville_arrivee__in=list_of_destination
            ).order_by('date_depart').values(
                "ville_depart", "ville_arrivee", "date_depart", "date_arrivee", "prix_unitaire", "id"
            ))
            print("filtre sans transport", list(Voyages.objects.filter(
                date_depart=today,
                ville_depart__in=list_of_depart,
                ville_arrivee__in=list_of_destination
            ).order_by('date_depart').values(
                "ville_depart", "ville_arrivee", "date_depart", "date_arrivee", "prix_unitaire", "id"
            )))

            print("le filtre avec transport", list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=today,
                ville_depart__in=list_of_depart,
                ville_arrivee__in=list_of_destination
            ).order_by('date_depart').values(
                "ville_depart", "ville_arrivee", "date_depart", "date_arrivee", "prix_unitaire", "id"
            )))
            
            if len(result) >= 1: 
                prix_total = result[0]['prix_unitaire'] * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) )
            elif len(result) == 0 and len(result_demain) >= 1:
                prix_total = result_demain[0]['prix_unitaire'] * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) )
            elif len(result) == 0 and len(result_demain) == 0 and len(result_hier) >= 1:
                prix_total = result_hier[0]['prix_unitaire'] * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) )
            else:
                prix_total = 0


            for dataset in [result_hier, result, result_demain]:
                for i in range(len(dataset)):
                    dataset[i]['heures'] = int(convert(dataset[i]['date_arrivee'].timestamp() - dataset[i]['date_depart'].timestamp())[0])
                    dataset[i]['minutes'] = int(convert(dataset[i]['date_arrivee'].timestamp() - dataset[i]['date_depart'].timestamp())[1])
                    dataset[i]['second'] = int(convert(dataset[i]['date_arrivee'].timestamp() - dataset[i]['date_depart'].timestamp())[2])

            list_of_date = dataSend['date_depart'][0].split('-')

            request.session['results_aller'] = json.dumps(result, default=str)
            request.session['date_depart'] = dataSend['date_depart'][0]
            request.session['date_retour'] = dataSend['date_retour'][0]
            request.session['nombre_adultes'] = dataSend['nbr_adl'][0]
            request.session['nombre_enfants'] = dataSend['nbr_enf'][0]
            request.session['nombre_bagages'] = dataSend['nbr_bga'][0]
            request.session['voyage_id_aller'] = result[0]['id'] if result else None
            request.session['prix_total'] = prix_total

            resultat_full = {
                "result_hier": result_hier,
                "result": result,
                "result_demain": result_demain,
             }
            result_by_day = {
                "hier": result_hier,
                "aujourdhui": result,
                "demain": result_demain
            }
            print("result_hier", result_hier)
            print("result", result)
            print("result_demain", result_demain)
            context = {
                "result": resultat_full["result"],
                "result_demain": resultat_full["result_demain"],
                "result_hier": resultat_full["result_hier"],
                "ville_depart": dataSend['depart'][0],
                "ville_arrivee": dataSend['destination'][0],
                "nombre_enfants": dataSend['nbr_enf'][0],
                "nombre_adultes": dataSend['nbr_adl'][0],
                "nombre_bagages": dataSend['nbr_bga'][0],
                "jour_avant": get_weekday(today - timedelta(days=1)),
                "jour_apres": get_weekday(today + timedelta(days=1)),
                "jour": get_weekday(today),
                "mois": get_month(str(int(list_of_date[1]))),
                "num_du_jour": int(list_of_date[2]),
                "num_du_jour_avant": int(list_of_date[2]) - 1,
                "num_du_jour_apres": int(list_of_date[2]) + 1,
                "date_depart": dataSend['date_depart'][0],
                "prix_total": prix_total * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) ),
                "timestamp": int(datetime.timestamp(datetime.now())),
            }
            return render(request, 'html/choix_du_voyage.html', context=context)

        elif dataSend['trip'][0] == "retour":
            result_hier = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=yesterday,
                ville_depart__in=list_of_depart
            ).exclude(ville_arrivee__in=list_of_depart)
            .filter(ville_arrivee__in=list_of_destination)
            .order_by('date_depart').values())

            result = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=today,
                ville_depart__in=list_of_depart
            ).exclude(ville_arrivee__in=list_of_depart)
            .filter(ville_arrivee__in=list_of_destination)
            .order_by('date_depart').values())

            result_demain = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_depart=tomorrow,
                ville_depart__in=list_of_depart
            ).exclude(ville_arrivee__in=list_of_depart)
            .filter(ville_arrivee__in=list_of_destination)
            .order_by('date_depart').values())

            result_retour = list(Voyages.objects.filter(
                transport__places_disponibles__gt=0,
                transport__isnull=False,
                date_arrivee__gt=tomorrow,
                ville_depart__in=list_of_destination,
                ville_arrivee__in=list_of_depart
            ).order_by('date_depart').values())

            if result :
                prix_total = (result[0]['prix_unitaire'] + result_retour[0]['prix_unitaire']) * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) )
            elif not result and result_demain:
                prix_total = (result_demain[0]['prix_unitaire'] + result_retour[0]['prix_unitaire']) * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) )
            elif not result and not result_demain and result_hier:
                prix_total = (result_hier[0]['prix_unitaire'] + result_retour[0]['prix_unitaire']) * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) )
            else:
                prix_total = 0

            request.session['results_aller'] = json.dumps(result, default=str)
            request.session['results_retour'] = json.dumps(result_retour, default=str)
            request.session['date_depart'] = dataSend['date_depart'][0]
            request.session['date_retour'] = dataSend['date_retour'][0]
            request.session['nombre_adultes'] = dataSend['nbr_adl'][0]
            request.session['nombre_enfants'] = dataSend['nbr_enf'][0]
            request.session['nombre_bagages'] = dataSend['nbr_bga'][0]
            request.session['voyage_id_aller'] = result[0]['id'] if result else None
            request.session['voyage_id_retour'] = result_retour[0]['id'] if result_retour else None
            request.session['prix_total'] = prix_total
            # Calcul des heures, minutes et secondes pour chaque voyage
            
            for dataset in [result_hier, result, result_demain]:
                for i in range(len(dataset)):
                    dataset[i]['heures'] = int(convert(dataset[i]['date_arrivee'].timestamp() - dataset[i]['date_depart'].timestamp())[0])
                    dataset[i]['minutes'] = int(convert(dataset[i]['date_arrivee'].timestamp() - dataset[i]['date_depart'].timestamp())[1])
                    dataset[i]['second'] = int(convert(dataset[i]['date_arrivee'].timestamp() - dataset[i]['date_depart'].timestamp())[2])

            for i in range(len(result_retour)):
                result_retour[i]['heures'] = int(convert(result_retour[i]['date_arrivee'].timestamp() - result_retour[i]['date_depart'].timestamp())[0])
                result_retour[i]['minutes'] = int(convert(result_retour[i]['date_arrivee'].timestamp() - result_retour[i]['date_depart'].timestamp())[1])
                result_retour[i]['second'] = int(convert(result_retour[i]['date_arrivee'].timestamp() - result_retour[i]['date_depart'].timestamp())[2])

            list_of_date = dataSend['date_depart'][0].split('-')
            list_of_date_retour = dataSend['date_retour'][0].split('-')

            resultat_full = {
                "result_hier": result_hier,
                "result": result,
                "result_demain": result_demain,
             }

            result_by_day = {
                "hier": result_hier,
                "aujourdhui": result,
                "demain": result_demain
            }
            print("result_hier", result_hier)
            print("result", result)
            print("result_demain", result_demain)
            print("result_retour", result_retour)

            context = {
                "result": resultat_full["result"],
                "result_demain": resultat_full["result_demain"],
                "result_hier": resultat_full["result_hier"],
                "result_retour": result_retour,
                "result_by_day": result_by_day,
                "ville_depart": dataSend['depart'][0],
                "ville_arrivee": dataSend['destination'][0],
                "nombre_enfants": dataSend['nbr_enf'][0],
                "nombre_adultes": dataSend['nbr_adl'][0],
                "nombre_bagages": dataSend['nbr_bga'][0],
                "jour_avant": get_weekday(today - timedelta(days=1)),
                "jour_apres": get_weekday(today + timedelta(days=1)),
                "jour": get_weekday(today),
                "mois": get_month(str(int(list_of_date[1]))),
                "jour_retour": get_weekday(date_retour + timedelta(days=1)),
                "mois_retour": get_month(str(int(list_of_date_retour[1]))),
                "jour_retour_avant": get_weekday(date_retour),
                "jour_retour_apres": get_weekday(date_retour + timedelta(days=2)),
                "num_du_jour": int(list_of_date[2]),
                "num_du_jour_avant": int(list_of_date[2]) - 1,
                "num_du_jour_apres": int(list_of_date[2]) + 1,
                "num_du_jour_retour": int(list_of_date_retour[2]),
                "num_du_jour_retour_avant": int(list_of_date_retour[2]) - 1,
                "num_du_jour_retour_apres": int(list_of_date_retour[2]) + 1,
                "date_depart": dataSend['date_depart'][0],
                "date_retour": dataSend['date_retour'][0],
                "list_of_day" : [('hier', result_hier), ('aujourdhui', result), ('demain', result_demain)] ,
                "prix_total": prix_total * (int(dataSend['nbr_adl'][0]) + int(dataSend['nbr_enf'][0]) ),
                "timestamp": int(datetime.timestamp(datetime.now())),
            }
            return render(request, 'html/choix_du_voyage.html', context=context)

    else:
        return render(request, 'html/section.html', context={
            'current': current
        })

def infos_personnelles(request):
    if request.method == "POST":
        voyage_id_aller = request.POST.get("voyage_id_aller")
        voyage_id_retour = request.POST.get("voyage_id_retour")  # peut être None
        print("voyage_id_aller", voyage_id_aller)
        print("voyage_id_retour", voyage_id_retour)
        print(Voyages.objects.filter(id=1602).exists())
        voyage_aller = Voyages.objects.filter(id=voyage_id_aller).values().first()
        voyage_retour = Voyages.objects.filter(id=voyage_id_retour).values().first() if voyage_id_retour else None
        print("voyage_aller", voyage_aller)
        print("voyage_retour", voyage_retour)
        if not voyage_aller:
            return HttpResponseForbidden("Voyage aller non trouvé.")
        
        request.session['selected_aller'] = json.dumps([voyage_aller], default=str)
        request.session['voyage_id_aller'] = voyage_aller["id"]

        if voyage_retour:
            request.session['selected_retour'] = json.dumps([voyage_retour], default=str)
            request.session['voyage_id_retour'] = voyage_retour["id"]
        else:
            request.session['results_retour'] = json.dumps([], default=str)

        return render(request, "html/infos_personnelles.html")
    return redirect("home")


def reservation(request):
    if request.method == "POST":
        # Champs client
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        email = request.POST.get("email")
        telephone = request.POST.get("telephone")
        adresse = request.POST.get("adresse")

        # Champs aller
        selected_aller_json = request.session.get("selected_aller")

        if selected_aller_json:
            try:
                selected_aller = json.loads(selected_aller_json)[0]  # On prend le premier élément de la liste
            except Exception as e:
                print("Erreur lors du json.loads :", e)
                selected_aller = {}

        else:
            selected_aller = {}
        
        print("selected_aller", selected_aller)


        aller = {
                    "ville_depart": selected_aller.get("ville_depart"),
                    "ville_arrivee": selected_aller.get("ville_arrivee"),
                    "date_depart": selected_aller.get("date_depart").split(" ")[0] if selected_aller.get("date_depart") else None,
                    "date_arrivee": selected_aller.get("date_arrivee").split(" ")[0] if selected_aller.get("date_arrivee") else None,
                    "prix_unitaire": selected_aller.get("prix_unitaire"),
                }

        # Champs retour (facultatif)
        retour = {
            "ville_depart": request.session.get("ville_depart_retour"),
            "ville_arrivee": request.session.get("ville_arrivee_retour"),
            "date_retour": request.session.get("date_retour"),
            "date_retour_arrivee": request.session.get("date_retour_arrivee"),
            "prix_unitaire": request.session.get("prix_unitaire")  # tu peux mettre un autre champ si retour différent
        }

        # Champs généraux
        nb_adultes = request.session.get("nombre_adultes", "0")
        nb_enfants = request.session.get("nombre_enfants", "0")
        nb_bagages = request.session.get("nombre_bagages", "0")

        # Formatage des dates (sécurisé)
        if aller["date_depart"] and aller["date_arrivee"]:
            try:
                aller["date_depart"] = datetime.fromisoformat(aller["date_depart"]).strftime("%Y-%m-%d")
                aller["date_arrivee"] = datetime.fromisoformat(aller["date_arrivee"]).strftime("%Y-%m-%d")
            except Exception as e:
                print("❌ Erreur format date aller :", e)
        else:
            print("❌ Dates aller manquantes ou mal formatées", aller)

        if retour.get("date_retour") and retour.get("date_retour_arrive"):
            # Assure que les dates de retour sont présentes avant de les formater
            try:
                
                retour["date_retour"] = datetime.fromisoformat(retour["date_retour"]).strftime("%Y-%m-%d")
                retour["date_retour_arrivee"] = datetime.fromisoformat(retour["date_retour_arrivee"]).strftime("%Y-%m-%d")
            except Exception as e:
                print("❌ Erreur format date retour :", e)
        else:
            print("❌ Dates retour manquantes ou mal formatées", retour)

        # Stockage dans la session
        request.session["nom"] = nom
        request.session["prenom"] = prenom
        request.session["email"] = email
        request.session["telephone"] = telephone
        request.session["adresse"] = adresse

        for key, value in aller.items():
            request.session[key] = value

        if retour.get("date_retour"):
            for key, value in retour.items():
                request.session[key] = value

        request.session["nombre_adultes"] = nb_adultes
        request.session["nombre_enfants"] = nb_enfants
        request.session["nombre_bagages"] = nb_bagages

        # Création du dictionnaire final pour affichage
        infos = {
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "telephone": telephone,
            "adresse": adresse,
            "ville_depart": aller["ville_depart"],
            "ville_arrivee": aller["ville_arrivee"],
            "date_depart": aller["date_depart"],
            "date_arrivee": aller["date_arrivee"],
            "prix_unitaire": aller["prix_unitaire"],
            "nombre_adultes": nb_adultes,
            "nombre_enfants": nb_enfants,
            "nombre_bagages": nb_bagages
        }

        if retour.get("date_retour"):
            infos.update({
                "ville_depart_retour": retour["ville_depart"],
                "ville_arrivee_retour": retour["ville_arrivee"],
                "date_retour": retour["date_retour"],
                "date_retour_arrivee": retour["date_retour_arrivee"],
                "prix_retour": retour["prix_unitaire"]
            })

        print("✅ Informations de réservation :", infos)
        return render(request, "html/reservation.html", {"infos": infos})

    return redirect("home")
    

def finaliser_reservation(request):
    print("finaliser_reservation called")

    if request.method == "POST":
        print("finaliser_reservation POST request")

        # Récupération des données aller
        ville_depart = request.POST.get("ville_depart")
        ville_arrivee = request.POST.get("ville_arrivee")
        date_depart = request.POST.get("date_depart")
        date_arrivee = request.POST.get("date_arrivee")
        adultes = request.POST.get("adultes")
        enfants = request.POST.get("enfants")
        bagages = request.POST.get("bagages")
        print("les adultes", adultes)
        print("les enfants", enfants)
        print("les bagages", bagages)

        # Sauvegarde dans la session
        request.session["ville_depart"] = ville_depart
        request.session["ville_arrivee"] = ville_arrivee
        request.session["date_depart"] = date_depart
        request.session["date_arrivee"] = date_arrivee
        request.session["adultes"] = adultes
        request.session["enfants"] = enfants
        request.session["bagages"] = bagages

        # Données retour (si présent)
        date_retour_depart = request.POST.get("date_retour")
        date_retour_arrivee = request.POST.get("date_retour_arrivee")
        ville_depart_retour = request.POST.get("ville_depart_retour")
        ville_arrivee_retour = request.POST.get("ville_arrivee_retour")
        prix_retour = request.POST.get("prix_retour") or "0"

        # Sauvegarde si les données retour existent
        if date_retour_depart and date_retour_arrivee:
            request.session["date_retour_depart"] = date_retour_depart
            request.session["date_retour_arrivee"] = date_retour_arrivee
            request.session["ville_depart_retour"] = ville_depart_retour
            request.session["ville_arrivee_retour"] = ville_arrivee_retour
            request.session["prix_retour"] = prix_retour

        # Récupération infos client
        request.session["nom"] = request.POST.get("nom")
        request.session["prenom"] = request.POST.get("prenom")
        request.session["email"] = request.POST.get("email")
        request.session["telephone"] = request.POST.get("telephone")
        request.session["adresse"] = request.POST.get("adresse")

        # Construction du récapitulatif
        prix_aller = int(request.session.get("prix_unitaire", "0"))
        prix_retour = int(prix_retour) if prix_retour else 0
        total = prix_aller + prix_retour
        print("client id", settings.PAYPAL_CLIENT_ID)
        print("secret key", settings.PAYPAL_SECRET_KEY)

        reservation_details = {
            "ville_depart": ville_depart,
            "ville_arrivee": ville_arrivee,
            "date_depart": date_depart,
            "date_arrivee": date_arrivee,
            "prix_aller": prix_aller,
            "ville_depart_retour": ville_depart_retour,
            "ville_arrivee_retour": ville_arrivee_retour,
            "date_retour_depart": date_retour_depart,
            "date_retour_arrivee": date_retour_arrivee,
            "prix_retour": prix_retour,
            "prix_total": f"{total:.2f}",
            "nom": request.session["nom"],
            "prenom": request.session["prenom"],
            "email": request.session["email"],
            "telephone": request.session["telephone"],
            "adresse": request.session["adresse"],
            "adultes": adultes,
            "enfants": enfants,
            "bagages": bagages,
            "PAYPAL_CLIENT_ID": settings.PAYPAL_CLIENT_ID,
            "PAYPAL_SECRET_KEY": settings.PAYPAL_SECRET_KEY,
            "PAYPAL_MODE": settings.PAYPAL_MODE,
        }

        return render(request, "html/resume.html", reservation_details)

    return redirect("reservation")


# Ajout d'un paiement via paypal
def payment_page(request):
    return render(request, "html/paiement/payment.html", {"amount": 10.00})  # Montant à payer

@csrf_exempt
def payment_complete(request):
    if request.method == "POST":
        # Ici tu peux ajouter une vérification du paiement si besoin
        # Tu peux aussi enregistrer un statut "Réservé/Paye" sur le voyage
        print("✅ Paiement reçu avec succès")
        return JsonResponse({"status": "success"})




@csrf_exempt
def lancer_paiement(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        telephone = data.get('telephone')
        montant = data.get('montant')
        operateur = data.get('operateur')

        resultat = payer(telephone, montant, operateur)
        return JsonResponse(resultat)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def generate_pdf(request):
    # Création ou récupération du User
    if request.method != "GET":
        return HttpResponse("❌ Méthode non autorisée. Cette vue attend une redirection après paiement PayPal.", status=405)
    
    email = request.session.get("email")
    prenom = request.session.get("prenom")
    nom = request.session.get("nom")

    user, _ = User.objects.get_or_create(
        email=email,
        defaults={"first_name": prenom, "last_name": nom, "email": email}
    )

    voyageur, _ = Voyageurs.objects.get_or_create(
        user=user,
        defaults={
            "firstname": prenom,
            "name": nom,
            "email": email,
            "password_reset_required": True
        }
    )
    voyageur.password_reset_required = True
    voyageur.save()

    mot_de_passe_temporaire = User.objects.make_random_password(length=10)
    request.session["mot_de_passe_temp"] = mot_de_passe_temporaire
    user.set_password(mot_de_passe_temporaire)
    user.save()

    # Réservation aller et retour
    voyage_ids = [request.session.get("voyage_id_aller"), request.session.get("voyage_id_retour")]

    for vid in voyage_ids:
        if vid:
            try:
                voyage = Voyages.objects.get(id=vid)

                # Réservation unique
                Reservation.objects.get_or_create(
                    voyageur=voyageur,
                    voyage=voyage
                )

                # ✅ Mise à jour des places et bagages
                nb_adultes = int(request.session.get("adultes", 0))
                nb_enfants = int(request.session.get("enfants", 0))
                nb_bagages = int(request.session.get("bagages", 0))
                total_passagers = nb_adultes + nb_enfants

                transport = getattr(voyage, "transport", None)
                if transport:
                    if (
                        transport.places_disponibles >= total_passagers
                        and transport.bagages_disponibles >= nb_bagages
                    ):
                        transport.places_disponibles -= total_passagers
                        transport.bagages_disponibles -= nb_bagages

                        if transport.places_disponibles <= 0 or transport.bagages_disponibles <= 0:
                            transport.disponible = False

                        transport.save()
                    else:
                        logger.warning(f"❌ Pas assez de ressources pour le transport {transport.id}")
                        return HttpResponse("❌ Désolé, il n’y a plus assez de places ou de bagages disponibles pour ce voyage.")

                else:
                    logger.warning(f"⚠️ Aucun transport associé au voyage {voyage.id}")
                    return HttpResponse("❌ Désolé, il n’y a plus de transport disponible à cette date.")


                # Création message tchat
                chauffeur = voyage.transporteurs
                if chauffeur:
                    if not MessageClientChauffeur.objects.filter(voyageur=voyageur, transporteur=chauffeur).exists():
                        MessageClientChauffeur.objects.create(
                            voyageur=voyageur,
                            transporteur=chauffeur,
                            contenu="Bonjour, j’ai réservé votre trajet.",
                            expediteur="voyageur"
                        )
            except Voyages.DoesNotExist:
                logger.warning(f"Voyage ID {vid} non trouvé")

    # Contexte PDF
    context = {
        "titre": "Preuve de la reservation de voyage",
        "date": now().strftime("%Y-%m-%d"),
        "heure": now().strftime("%H:%M"),
        "Reserveur": request.session.get("nom", "Inconnu") + " " + request.session.get("prenom", ""),
        "email": request.session.get("email", "Inconnu"),
        "telephone": request.session.get("telephone", "Inconnu"),
        "adresse": request.session.get("adresse", "Inconnue"),
        "ville_depart": request.session.get("ville_depart", "Inconnue"),
        "ville_arrivee": request.session.get("ville_arrivee", "Inconnue"),
        "date_depart": request.session.get("date_depart", "Inconnue"),
        "date_arrivee": request.session.get("date_arrivee", "Inconnue"),
        "ville_depart_retour": request.session.get("ville_depart_retour", ""),
        "ville_arrivee_retour": request.session.get("ville_arrivee_retour", ""),
        "date_retour_depart": request.session.get("date_retour", ""),
        "date_retour_arrivee": request.session.get("date_retour_arrivee", ""),
        "nombre_adultes": request.session.get("adultes", "0"),
        "nombre_enfants": request.session.get("enfants", "0"),
        "nombre_bagages": request.session.get("bagages", "0"),
        "prix_aller": request.session.get("prix_unitaire", "0 fcfa"),
        "prix_retour": request.session.get("prix_retour", "0 fcfa"),
        "prix_total": int(request.session.get("prix_unitaire", "0") or 0) + int(request.session.get("prix_retour", "0") or 0),
        "mot_de_passe_temp": request.session.get("mot_de_passe_temp", "Non généré"),
        "remarques": "Le voyage a été réservé avec succès. Merci de votre confiance."
    }

    # Génération du PDF
    template = get_template("html/recap_pdf.html")
    html = template.render(context)
    filename = f"ticket_{now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, "tickets", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as f:
        pisa_status = pisa.CreatePDF(html, dest=f)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF")

    # Sauvegarde du PDF
    try:
        with open(filepath, "rb") as f:
            voyageur.ticket_pdf.save(filename, File(f), save=True)
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du PDF pour le voyageur : {e}")

    with open(filepath, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@staff_member_required
def import_excel_view(request):
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            path = os.path.join("transport", excel_file.name)
            
            # Enregistre le fichier dans transport/
            with open(path, "wb+") as dest:
                for chunk in excel_file.chunks():
                    dest.write(chunk)

            # Exécuter FillData avec l'utilisateur courant
            FillData(path, user=request.user).charge()
            messages.success(request, "✅ Importation réussie")
            return redirect("/admin/")
    else:
        form = ExcelImportForm()
    
    historiques = HistoriqueImport.objects.order_by('-date_import')[:10]

    return render(request, "admin/global_excel_import.html", {
        "form": form,
        "historiques": historiques
    })

# la vue change de mot de passe est une vue qui concerne que le voyageur
# ==========================
# 💬 Changer le mot de passe
# ==========================

@login_required

@login_required
def changer_mot_de_passe(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("changer_mot_de_passe")

        user = request.user
        user.set_password(new_password)
        user.save()

        # Désactive le flag si c'est un voyageur ou un chauffeur
        if hasattr(user, 'voyageurs'):
            user.voyageurs.password_reset_required = False
            user.voyageurs.save()
            next_login = "login_user"
        elif hasattr(user, 'transporteurs'):
            user.transporteurs.password_reset_required = False
            user.transporteurs.save()
            next_login = "login_chauffeur"
        else:
            next_login = "user_login"  # fallback

        messages.success(request, "Mot de passe modifié avec succès. Veuillez vous reconnecter.")
        return redirect(next_login)
    # ⬇️ Ajout du contexte pour afficher le rôle dans le template
    user = request.user
    role = None
    if hasattr(user, 'voyageurs'):
        role = "voyageur"
    elif hasattr(user, 'transporteurs'):
        role = "chauffeur"

    return render(request, "user_app/change_password.html", {"role": role})
# les vues pour les chauffeurs

# ==========================
# 💬 Tchat Vue
# ==========================


@login_required
def tchat(request, transporteur_id):
    user = request.user
    voyageur = None
    transporteur = None
    messages = None

    if hasattr(user, 'voyageurs'):
        voyageur = user.voyageurs
        transporteur = get_object_or_404(Transporteurs, id=transporteur_id)

        messages = MessageClientChauffeur.objects.filter(
            voyageurs=voyageur, transporteurs=transporteur
        ).order_by('timestamp')

        if request.method == 'POST':
            contenu = request.POST.get("contenu")
            if contenu.strip():
                MessageClientChauffeur.objects.create(
                    voyageurs=voyageur,
                    transporteurs=transporteur,
                    message=contenu,
                    sender="voyageur"
                )
            return redirect('tchat', transporteur_id=transporteur.id)

    elif hasattr(user, 'transporteurs'):
        transporteur = user.transporteurs
        voyageur_id = request.GET.get("voyageur_id")
        voyageur = get_object_or_404(Voyageurs, id=voyageur_id)

        messages = MessageClientChauffeur.objects.filter(
            voyageurs=voyageur, transporteurs=transporteur
        ).order_by('timestamp')

        if request.method == 'POST':
            contenu = request.POST.get("contenu")
            if contenu.strip():
                MessageClientChauffeur.objects.create(
                    voyageurs=voyageur,
                    transporteurs=transporteur,
                    message=contenu,
                    sender="chauffeur"
                )
            return redirect(f"/tchat/{transporteur.id}/?voyageur_id={voyageur.id}")

    else:
        return redirect("user_login")  # fallback si aucun rôle détecté

    return render(request, 'user_app/chat_responsive.html', {
        'voyageur': voyageur,
        'transporteur': transporteur,
        'messages': messages,
    })

# ==========================
# 👤 Auth Utilisateur & Chauffeur
# ==========================


def user_login(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)

            if getattr(settings, "DEBUG_SKIP_2FA", False):
                return redirect('dashboard')  # skip 2FA pour test local

            code = str(random.randint(100000, 999999))
            VerificationCode.objects.update_or_create(
                user=user,
                defaults={'code': code}
            )
            request.session['pre_auth_user'] = user.id
            return redirect('verify_code')
        else:
            # 🔥 Ajout d'un message d'erreur clair
            messages.error(request, "Email ou mot de passe invalide. Veuillez réessayer.")
            return render(request, 'user_app/usr_login.html')

        messages.error(request, "Email ou mot de passe invalide.")
    return render(request, 'user_app/usr_login.html')


# ==========================
# 👤 Auth Chauffeur
# ==========================

def login_chauffeur(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            code = str(random.randint(100000, 999999))
            print(code)
            VerificationCode.objects.update_or_create(
                user=user,
                defaults={'code': code}
            )
            request.session['pre_auth_chauffeur'] = user.id
            return redirect('chauffeur_app/verify_chauffeur')
    return render(request, 'chauffeur_app/cha_login.html')


def verify_code(request):
    print("🟡 Entrée dans verify_code")

    # 🔧 Mode debug : désactiver 2FA pour tests locaux
    if getattr(settings, "DEBUG_SKIP_2FA", False):
        print("🛠️ DEBUG_SKIP_2FA actif")
        user_id = request.session.get("pre_auth_user")
        print("🔎 ID utilisateur (session) :", user_id)

        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            login(request, user)
            print("✅ Utilisateur connecté :", user)

            # 🔍 Vérifie le rôle
            if Voyageurs.objects.filter(user=user).exists():
                print("🎯 Rôle : VOYAGEUR")
                return redirect("dashboard")
            elif Transporteurs.objects.filter(user=user).exists():
                print("🎯 Rôle : TRANSPORTEUR")
                return redirect("dashboard_chauffeur")

            print("🚨 Aucun rôle trouvé pour cet utilisateur")
            messages.error(request, "Utilisateur sans rôle associé.")
            return redirect("login")

    # 🔐 Validation du code saisi (POST)
    if request.method == "POST":
        print("📩 POST reçu - tentative de vérification du code")
        code_saisi = request.POST.get("code")
        user_id = request.session.get("pre_auth_user")
        print("🔍 Code saisi :", code_saisi)
        print("🔍 ID utilisateur (session) :", user_id)

        if not user_id:
            print("❌ Session expirée")
            messages.error(request, "Session expirée. Veuillez vous reconnecter.")
            return redirect("login")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        print("✅ Utilisateur récupéré :", user)

        try:
            verif = VerificationCode.objects.get(user=user)
            print("✅ Code de vérification trouvé :", verif.code)
        except VerificationCode.DoesNotExist:
            print("❌ Code de vérification non trouvé")
            messages.error(request, "Code non trouvé. Veuillez vous reconnecter.")
            return redirect("login")

        if code_saisi == verif.code:
            print("✅ Code correct")
            login(request, user)
            del request.session["pre_auth_user"]

            # Redirection selon le rôle
            if Voyageurs.objects.filter(user=user).exists():
                print("🎯 Rôle détecté : VOYAGEUR")
                return redirect("dashboard")
            elif Transporteurs.objects.filter(user=user).exists():
                print("🎯 Rôle détecté : TRANSPORTEUR")
                return redirect("dashboard_chauffeur")
            else:
                print("❌ Rôle non détecté dans la base")
                messages.error(request, "Rôle inconnu. Contactez l’administrateur.")
                return redirect("login")
        else:
            print("❌ Code incorrect")
            messages.error(request, "Code incorrect. Réessayez.")

    return render(request, "user_app/usr_verify_code.html")


# ==========================
# 📊 Dashboards
# ==========================

@login_required

def dashboard(request):
    user = request.user
    try:
        voyageur = Voyageurs.objects.get(user=user)
    except Voyageurs.DoesNotExist as e:
        print(f"❌ Voyageur non trouvé pour l'utilisateur {user.id}: {e}")
        messages.error(request, "Vous devez être un voyageur pour accéder à ce tableau de bord.")
        return redirect("user_login")

    # Toutes les réservations de ce voyageur
    reservations = Reservation.objects.filter(voyageur=voyageur).select_related('voyage', 'voyage__transporteurs')

    # Nombre total de voyages
    travel_count = reservations.count()

    # Total dépensé
    total_spent = sum(r.voyage.prix_unitaire for r in reservations)

    # Prochain voyage
    next_travel = (
        reservations.filter(voyage__date_depart__gte=now())
        .order_by('voyage__date_depart')
        .first()
    )

    # 5 derniers voyages
    recent_travels = reservations.order_by('-voyage__date_depart')[:5]

    # Données pour le graphique (dépenses par mois)
    monthly_spending = {}
    for res in reservations:
        key = res.voyage.date_depart.strftime('%Y-%m')
        monthly_spending[key] = monthly_spending.get(key, 0) + res.voyage.prix_unitaire
    

    # Convertir les données en listes pour le graphique

    if len(list(monthly_spending.keys())) > 0:
        depense_dates = list(monthly_spending.keys())
        depense_values = list(monthly_spending.values())
    else :
        depense_dates = ['2025-06-01', '2025-06-02', '2025-06-03']
        depense_values = [100, 200, 150]

    context = {
        "user": user,
        "travel_count": travel_count,
        "total_spent": total_spent,
        "next_travel": next_travel.voyage if next_travel else None,
        "recent_travels": [r.voyage for r in recent_travels],
        "ticket_path": voyageur.ticket_pdf.url if voyageur.ticket_pdf else None,
        "depense_dates": json.dumps(depense_dates),
        "depense_values": json.dumps(depense_values),
    }
    return render(request, "user_app/usr_dashboard.html", context)


@login_required
def dashboard_chauffeur(request):
    user = request.user
    chauffeur = get_object_or_404(Transporteurs, user=user)

    # Voyages du chauffeur
    voyages = Voyages.objects.filter(transporteurs=chauffeur).order_by('-date_depart')

    # 5 derniers voyages
    last_5_voyages = voyages[:5]

    # Total des gains
    total_earned = sum(v.prix_unitaire for v in voyages)

    # Liste des voyageurs associés
    associations = Asso_trans_voyageur.objects.filter(transporteurs=chauffeur)
    voyageurs = [asso.voyageurs for asso in associations]

    # Messagerie attachée
    tchat_links = [
        {
            'voyageur': v,
            'url': f"/tchat/{chauffeur.id}/?voyageur_id={v.id}"
        }
        for v in voyageurs
    ]

    context = {
        'chauffeur': chauffeur,
        'travel_count': voyages.count(),
        'total_earned': total_earned,
        'last_voyages': last_5_voyages,
        'tchat_links': tchat_links,
    }

    return render(request, "chauffeur_app/cha_dashboard.html", context)

# ✅ Télécharger liste passagers en PDF
@login_required
def telecharger_passagers_pdf(request):
    user = request.user

    # Sécurité : l'utilisateur doit être un transporteur
    try:
        chauffeur = Transporteurs.objects.get(user=user)
    except Transporteurs.DoesNotExist:
        raise PermissionDenied("Accès refusé. Réservé aux chauffeurs.")

    # Récupérer les voyageurs associés via la table de liaison
    associations = Asso_trans_voyageur.objects.filter(transporteurs=chauffeur)
    voyageurs = [asso.voyageurs for asso in associations]

    # Création du PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Liste des passagers associés à {chauffeur.firstname} {chauffeur.name}")

    y = 780
    for v in voyageurs:
        line = f"- {v.firstname} {v.name} ({v.email})"
        p.drawString(100, y, line)
        y -= 20
        if y < 50:  # Sauter à une nouvelle page si plus de place
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 800

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="liste_passagers.pdf")


def register_user(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        name = request.POST.get('nom')
        firstname = request.POST.get('prenom')
        email = request.POST.get('email')
        password_temp = request.POST.get('password')

        # Vérification des champs communs
        if not all([role, name, firstname, email, password_temp]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('register_user')

        # Vérifier unicité de l'email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Un compte avec cet email existe déjà.")
            return redirect('register_user')

        # Sécurité minimale mot de passe
        if len(password_temp) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
            return redirect('register_user')

        # Création de l'utilisateur
        user = User.objects.create_user(email=email, password=password_temp)
        user.first_name = firstname
        user.last_name = name
        user.role = role
        user.save()

        # Inscription d’un voyageur
        if role == 'voyageur':
            Voyageurs.objects.create(
                user=user,
                name=name,
                firstname=firstname,
                email=email
            )
            messages.success(request, "Voyageur enregistré avec succès.")
            return redirect('user_login')

        # Inscription d’un chauffeur
        elif role == 'chauffeur':
            date_de_naissance = request.POST.get('date_de_naissance')
            adresse = request.POST.get('adresse')
            ville = request.POST.get('ville')
            permis = request.POST.get('permis')
            phone = request.POST.get('phone')

            if not all([date_de_naissance, adresse, ville, permis, phone]):
                messages.error(request, "Tous les champs sont obligatoires pour le chauffeur.")
                return redirect('register_user')

            try:
                date_obj = datetime.strptime(date_de_naissance, '%Y-%m-%d')
            except ValueError:
                messages.error(request, "Format de date de naissance invalide. Utilisez AAAA-MM-JJ.")
                return redirect('register_user')

            Transporteurs.objects.create(
                user=user,
                name=name,
                firstname=firstname,
                email=email,
                date_de_naissance=date_obj,
                adresse=adresse,
                ville=ville,
                permis=permis,
                phone=phone
            )
            messages.success(request, "Chauffeur enregistré avec succès.")
            return redirect('cha_login')

        # Cas invalide
        else:
            messages.error(request, "Rôle invalide.")
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect('register_user')

    return render(request, 'user_app/register_user.html')

def password_reset_voyageur(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST.get('email')
        new_password = request.POST.get('password')

        try:
            voyageur = Voyageurs.objects.get(email=email)
            user = voyageur.user
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Mot de passe mis à jour pour le voyageur.")
            return redirect('user_login')  # ou autre nom d’URL
        except Voyageurs.DoesNotExist:
            messages.error(request, "Aucun compte voyageur trouvé pour cet email.")
    
    return render(request, 'user_app/password_reset.html')

def password_reset_chauffeur(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST.get('email')
        new_password = request.POST.get('password')

        try:
            chauffeur = Transporteurs.objects.get(email=email)
            user = chauffeur.user
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Mot de passe mis à jour pour le chauffeur.")
            return redirect('login')
        except Transporteurs.DoesNotExist:
            messages.error(request, "Aucun compte chauffeur trouvé pour cet email.")

    return render(request, 'chauffeur_app/password_reset.html')


def about(request):
    """
        Cette fonction permet de parcourir 
        la page au sujet de nous
    """
    return render(request, 'html/about.html')

def homepage2(request):

    """
        cette fonction permet de s'orienter vers
        la deuxieme page du site internet 
    """
    return render(request, 'html/homepage-2.html')

def homepage3(request):

    """
        cette fonction permet de s'orienter vers
        la troisieme page du site internet
    """
    return render(request, 'html/homepage-3.html')

def custom_404_view(request, exception):
    """
        cette fonction permet de erreur 404
    """
    return render(request, "html/404.html", status=404)



def question(request):

    """
        la page de la foire aux questions
        qui réponds à la plus part des questions que
        se posent les users
    """

    return render(request, 'html/FAQ.html')

def contact(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if nom and email and message:
            send_mail(
                subject=f"Contact depuis le site de {nom}",
                message=message,
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )
            messages.success(request, "Votre message a bien été envoyé !")
            return redirect("contact")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    return render(request, "html/contact.html")


def comming_soon(request):
    
    """
        la fonction permet d'afficher 
        comming soon de la page
    """
    return render(request, 'html/comming-soon.html')

def career(request):
    
    """
        la fonction qui oriente vers la page carriere du site
    """
    return render(request, 'html/career.html')

def sign_in(request):
     """ la fonction qui permet de s'identifier """

     return render(request, 'html/sign-in.html')

def sign_up(request):
     """ la fonction qui permet de se deconnecter """

     return render(request, 'html/sign-up.html')

def team(request):

    return render(request, 'html/team.html')

def blog(request):
    """ Le blog entretenu par l'entreprise"""

    return render(request, 'html/blog.html')

def blog_single(request):

    return render(request, 'html/blog-single.html')

def privacy(request):

    return render(request, 'html/privacy-policy.html')

@staff_member_required
def vider_table_view(request):
    if request.method == "POST":
        form = ViderTableForm(request.POST)
        if form.is_valid():
            model_label = form.cleaned_data["modele"]
            CustomUser = get_user_model()

            if model_label == CustomUser._meta.label:
                # 🔁 Étape 1 : Supprimer les dépendances liées à CustomUser
                voyageurs_deleted = Voyageurs.objects.count()
                transporteurs_deleted = Transporteurs.objects.count()
                Voyageurs.objects.all().delete()
                Transporteurs.objects.all().delete()

                # 🔁 Étape 2 : Supprimer les utilisateurs non-admin
                users_to_delete = CustomUser.objects.filter(is_staff=False, is_superuser=False)
                count = users_to_delete.count()
                users_to_delete.delete()

                messages.success(request, f"✅ {count} utilisateurs supprimés. "
                                          f"({voyageurs_deleted} voyageurs et {transporteurs_deleted} transporteurs supprimés avant).")
            else:
                model = apps.get_model(model_label)
                count = model.objects.count()
                model.objects.all().delete()
                messages.success(request, f"✅ {count} enregistrements supprimés dans '{model._meta.verbose_name_plural}'.")

            return redirect("vider-table")
    else:
        form = ViderTableForm()

    return render(request, "admin/vider_table.html", {"form": form})
