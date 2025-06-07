from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from datetime import date, datetime, timedelta, time, timezone
from django.utils.timezone import now, localdate, make_aware
from .models import Voyages,MessageClientChauffeur, CustomUser, VerificationCode, Voyageurs, Transporteurs
from .utils import convert, get_weekday, get_month, safe_format_iso
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import get_template
from xhtml2pdf import pisa
from itertools import zip_longest
import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import random
from import_excel import FillData
from .forms import ExcelImportForm
import os
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.


def home(request):

    """cette fonction lance la page home du site
        le result est une liste qui content autant de dictionnaire que de voyage
        chaque dictionnaire contient les informations sur le voyage
    """
    current = date.today().strftime("%Y-%m-%d")
    # récupération de la date actuelle
    
    # filtrage des données
    # result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow)).filter(ville_depart__contains= 'LIBREVILLE').exclude(ville_arrivee='LIBREVILLE').values())
    
    # affichage des données
   
    if request.method == 'POST':
        dataSend = dict(request.POST)
        today =  datetime.strptime(dataSend['date_depart'][0], "%Y-%m-%d").date()
        try:
            date_retour = datetime.strptime(dataSend['date_retour'][0], "%Y-%m-%d").date()
        except:
            date_retour = None

        if dataSend['trip'][0] == "aller":

            # si le voyage est aller simple
            yesterday = today - timedelta(days=1)
            tomorrow = today + timedelta(days=1)

            # filtrage des données
            
            list_of_depart = [col.title() for col in dataSend['depart']]
            list_of_destination = [col.title() for col in dataSend['destination']]
            print("ville de départ :", list_of_depart)
            print("ville de destination :", list_of_destination)
            print("liste de destination :", Voyages.objects.filter(date_depart__range=(yesterday, tomorrow)).filter(ville_depart__in=list_of_depart).values())
            result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow))
                                         .filter(ville_depart__in=list_of_depart)
                                         .filter(ville_arrivee__in=list_of_destination)
                                         .order_by('date_depart')
                                         .values(
                                             "ville_depart",
                                             "ville_arrivee",
                                             "date_depart",
                                             "date_arrivee",
                                             "prix_unitaire",
                                             "id"
                                         )
                        )
            print(">>>>>>> les data de envoi :", result)
            for i in range(len(result)):
                
                result[i]['heures'] = int(convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[0])
                result[i]['minutes'] = int(convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[1])
                result[i]['second'] = int(convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[2])

            list_of_date = dataSend['date_depart'][0].split('-')
            # ... ton traitement existant ...
    
            request.session['results_aller'] = json.dumps(result, default=str) 
            request.session['date_depart'] = dataSend['date_depart'][0]
            request.session['date_retour'] = dataSend['date_retour'][0]
            request.session['nombre_adultes'] = dataSend['nbr_adl'][0]
            request.session['nombre_enfants'] = dataSend['nbr_enf'][0]
            request.session['nombre_bagages'] = dataSend['nbr_bga'][0]


            context = { 'result' : result, 
                       "ville_depart" : dataSend['depart'][0],
                       "ville_arrivee" : dataSend['destination'][0],
                       "nombre_enfants" : dataSend['nbr_enf'][0], 
                       "nombre_adultes" : dataSend['nbr_adl'][0], 
                       "nombre_bagages" : dataSend['nbr_bga'][0],
                       "jour_avant" : get_weekday(today - timedelta(days=1)),
                       "jour_apres" : get_weekday(today + timedelta(days=1)),
                       "jour" : get_weekday(today),
                       "mois" : get_month(str(int(list_of_date[1]))),
                       "num_du_jour" : int(list_of_date[2]),
                       "num_du_jour_avant" : int(list_of_date[2]) - 1,
                       "num_du_jour_apres" : int(list_of_date[2]) + 1,
                       "date_depart" : dataSend['date_depart'][0],
                       "timestamp" : int(datetime.timestamp(datetime.now())),
                      }
            return render(request,'html/choix_du_voyage.html' , context = context)
        # si le voyage est aller retour
        elif dataSend['trip'][0] == "retour":

            print("la date d'aujourd'hui :", today)
            yesterday = today - timedelta(days=1)
            print("la date d'hier :", yesterday)
            tomorrow = today + timedelta(days=1)
            print("la date de demain :", tomorrow)
            print("la data entre :", dataSend)

            

            # filtrage des données
            
            list_of_depart = [col.title() for col in dataSend['depart']]
            list_of_retour = [col.title() for col in dataSend['destination']]

            
            result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow))
                                         .filter(ville_depart__in=list_of_depart)
                                         .exclude(ville_arrivee__in=list_of_depart)
                                         .filter(ville_arrivee__in=list_of_retour)
                                         .order_by('date_depart')
                                         .values()
                        )
            result_retour = list(Voyages.objects.filter(date_arrivee__gt= tomorrow)
                                         .filter(ville_depart__in=list_of_retour)
                                         .filter(ville_arrivee__in=list_of_depart)
                                         .order_by('date_depart')
                                         .values()
                        )
            #if len(result_retour) == 0:
            #   return HttpResponse("Aucun voyage retour trouvé pour les critères spécifiés.", status=404)
            # filtrage des données
            print(">>>>>>> les data de envoi :", result)
            print(">>>>>>> les data de retour :", result_retour)
            
            request.session['results_aller'] = json.dumps(result, default=str) 
            request.session['results_retour'] = json.dumps(result_retour, default=str) 
            request.session['date_depart'] = dataSend['date_depart'][0]
            request.session['date_retour'] = dataSend['date_retour'][0]
            request.session['nombre_adultes'] = dataSend['nbr_adl'][0]
            request.session['nombre_enfants'] = dataSend['nbr_enf'][0]
            request.session['nombre_bagages'] = dataSend['nbr_bga'][0]
            
            for i in range(len(result)):
                
                result[i]['heures'] = int(convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[0])
                result[i]['minutes'] = int(convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[1])
                result[i]['second'] = int(convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[2])
            
            for i in range(len(result_retour)):
                result_retour[i]['heures'] = int(convert(result_retour[i]['date_arrivee'].timestamp() - result_retour[i]['date_depart'].timestamp())[0])
                result_retour[i]['minutes'] = int(convert(result_retour[i]['date_arrivee'].timestamp() - result_retour[i]['date_depart'].timestamp())[1])
                result_retour[i]['second'] = int(convert(result_retour[i]['date_arrivee'].timestamp() - result_retour[i]['date_depart'].timestamp())[2])

            list_of_date = dataSend['date_depart'][0].split('-')
            list_of_date_retour = dataSend['date_retour'][0].split('-')

            
            
            context = { 'result' : result, 
                       'result_retour' : result_retour,
                       "ville_depart" : dataSend['depart'][0],
                       "ville_arrivee" : dataSend['destination'][0],
                       "nombre_enfants" : dataSend['nbr_enf'][0], 
                       "nombre_adultes" : dataSend['nbr_adl'][0], 
                       "nombre_bagages" : dataSend['nbr_bga'][0],
                       "jour_avant" : get_weekday(today - timedelta(days=1)),
                       "jour_apres" : get_weekday(today + timedelta(days=1)),
                       "jour" : get_weekday(today),
                       "mois" : get_month(str(int(list_of_date[1]))),
                       "jour_retour" : get_weekday(date_retour + timedelta(days=1)),
                       "mois_retour" : get_month(str(int(list_of_date_retour[1]))),
                       "jour_retour_avant" : get_weekday(date_retour),
                       "jour_retour_apres" : get_weekday(date_retour + timedelta(days=2)),

                       "num_du_jour" : int(list_of_date[2]),
                       "num_du_jour_avant" : int(list_of_date[2]) - 1,
                       "num_du_jour_apres" : int(list_of_date[2]) + 1,
                       "num_du_jour_retour" : int(list_of_date_retour[2]),
                       "num_du_jour_retour_avant" : int(list_of_date_retour[2]) - 1,
                       "num_du_jour_retour_apres" : int(list_of_date_retour[2]) + 1,
                       "date_depart" : dataSend['date_depart'][0],
                       "date_retour" : dataSend['date_retour'][0],
                       "timestamp" : int(datetime.timestamp(datetime.now())),
                      }
            return render(request,'html/choix_du_voyage.html' , context = context)

    else:
        return render(request, 'html/section.html', context={
            'current': current
        })
    

def infos_personnelles(request):
    import json

    if request.method == "POST":
        selected_index = request.POST.get("selected_index")
        print("selected_index :", selected_index)

        if selected_index is None:
            return HttpResponse("Erreur : aucun index sélectionné", status=400)

        try:
            index = int(selected_index)
        except ValueError:
            return HttpResponse("Erreur : index non valide", status=400)

        result_allers = json.loads(request.session.get("results_aller", "[]"))
        result_retours = json.loads(request.session.get("results_retour", "[]"))

        if index >= len(result_allers):
            return HttpResponse("Erreur : index hors limite", status=400)
        print("result_allers :", result_allers)
        selected_aller = result_allers[index]
        print("selected_aller :", selected_aller)
        selected_retour = result_retours[index] if index < len(result_retours) else {}

        #  Convertir les string en datetime
        selected_aller["date_depart"] = datetime.fromisoformat(selected_aller["date_depart"]).strftime("%Y-%m-%d")
        selected_aller["date_arrivee"] = datetime.fromisoformat(selected_aller["date_arrivee"]).strftime("%Y-%m-%d")

        if "date_retour" in selected_retour and "date_retour_arrivee" in selected_retour:

            selected_retour["date_retour"] = datetime.fromisoformat(selected_retour["date_retour"]).strftime("%Y-%m-%d")
            selected_retour["date_retour_arrivee"] = datetime.fromisoformat(selected_retour["date_retour_arrivee"]).strftime("%Y-%m-%d")
        else:
            selected_retour["date_retour"] = None
            selected_retour["date_retour_arrivee"] = None

        # 🔎 Vérification stricte des champs obligatoires
        required_fields = ["ville_depart", "ville_arrivee", "date_depart", "date_arrivee", "prix_unitaire"]
        for field in required_fields:
            if field not in selected_aller or selected_aller[field] in [None, ""]:
                return HttpResponse(f"Erreur : champ aller manquant ou vide : {field}", status=400)

        # Enregistrement des infos aller dans la session
        for key in required_fields:
            request.session[key] = selected_aller[key]

        # ✅ Gestion du retour si existant
        if all(k in selected_retour for k in ["ville_depart", "ville_arrivee", "date_retour", "date_retour_arrivee"]):
            request.session["ville_depart_retour"] = selected_retour["ville_depart"]
            request.session["ville_arrive_retour"] = selected_retour["ville_arrivee"]
            request.session["date_retour"] = selected_retour["date_retour"]
            request.session["date_retour_arrivee"] = selected_retour["date_retour_arrivee"]
            request.session["prix_retour"] = selected_retour.get("prix_unitaire", "0")
        else:
            request.session["ville_depart_retour"] = ""
            request.session["ville_arrive_retour"] = ""
            request.session["date_retour"] = ""
            request.session["date_retour_arrive"] = ""
            request.session["prix_retour"] = ""

        # Pour affichage dans le formulaire
        request.session["selected_aller"] = json.dumps(selected_aller, default=str)
        request.session["selected_retour"] = json.dumps(selected_retour, default=str)

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
        aller = {
            "ville_depart": request.session.get("ville_depart"),
            "ville_arrivee": request.session.get("ville_arrivee"),
            "date_depart": request.session.get("date_depart"),
            "date_arrivee": request.session.get("date_arrivee"),
            "prix_unitaire": request.session.get("prix_unitaire")
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
        prix_aller = request.session.get("prix_unitaire", "0")
        total = (
            int(prix_aller) +
            int(prix_retour) if prix_retour else 0
        )

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
            "prix_total": f"{total} fcfa",
            "nom": request.session["nom"],
            "prenom": request.session["prenom"],
            "email": request.session["email"],
            "telephone": request.session["telephone"],
            "adresse": request.session["adresse"],
            "adultes": adultes,
            "enfants": enfants,
            "bagages": bagages,
        }

        print("Récapitulatif réservation :", reservation_details)
        print("=== CONTENU DU CONTEXTE RÉSUMÉ ===")
        for k, v in reservation_details.items():
            print(k, ":", v)

        return render(request, "html/resume.html", reservation_details)

    return redirect("reservation")

def generate_pdf(request):
    context = {
        "titre": "Preuve de la reservatioin de voyage",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "heure": datetime.now().strftime("%H:%M"),
        "Reserveur": request.session.get("nom", "Inconnu") + " " + request.session.get("prenom", "Inconnu"),
        "email": request.session.get("email", "Inconnu"),
        "telephone": request.session.get("telephone", "Inconnu"),
        "adresse": request.session.get("adresse", "Inconnue"),
        "objectif": "Achat d'un voyage à l'interieur du Gabon",
        "ville_depart": request.session.get("ville_depart", "Inconnu"),
        "ville_arrivee": request.session.get("ville_arrivee", "Inconnue"),
        "date_depart": request.session.get("date_depart", "Inconnue"),
        "date_arrivee": request.session.get("date_arrivee", "Inconnue"),
        "ville_depart_retour": request.session.get("ville_depart_retour", "Inconnue"),
        "ville_arrivee_retour": request.session.get("ville_arrivee_retour", "Inconnue"),
        "date_retour_depart": request.session.get("date_retour_depart", "Inconnue"),
        "date_retour_arrivee": request.session.get("date_retour_arrivee", "Inconnue"),
        "nombre_adultes": request.session.get("adultes", "0"),
        "nombre_enfants": request.session.get("enfants", "0"),
        "nombre_bagages": request.session.get("bagages", "0"),
        "prix_aller": request.session.get("prix_unitaire", "0 fcfa"),
        "prix_retour": request.session.get("prix_retour", "0 fcfa"),
        "prix_total": int(request.session.get("prix_unitaire") or "0") + int(request.session.get("prix_retour") or "0"),
        "remarques": "Le voyage a été réservé avec succès. Merci de votre confiance.",
    }

    template = get_template("html/recap_pdf.html")
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF")
    return response



@staff_member_required
def import_excel_view(request):
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            path = os.path.join("transport", excel_file.name)
            
            # Enregistrer le fichier dans transport/
            with open(path, "wb+") as dest:
                for chunk in excel_file.chunks():
                    dest.write(chunk)

            # Exécuter FillData
            FillData(path).charge()

            messages.success(request, "✅ Importation réussie")
            return redirect("/admin/")
    else:
        form = ExcelImportForm()
    
    return render(request, "admin/global_excel_import.html", {"form": form})

# les vues pour les chauffeurs

# ==========================
# 💬 Tchat Vue
# ==========================

@login_required
def tchat_vue(request, transporteur_id=None):
    user = request.user
    try:
        voyageur = Voyageurs.objects.get(user=user)
        role = 'voyageur'
    except Voyageurs.DoesNotExist:
        voyageur = None

    try:
        chauffeur = Transporteurs.objects.get(user=user)
        role = 'transporteur'
    except Transporteurs.DoesNotExist:
        chauffeur = None

    if role == 'voyageur':
        transporteur = get_object_or_404(Transporteurs, id=transporteur_id)
        messages = MessageClientChauffeur.objects.filter(
            voyageur=voyageur,
            transporteur=transporteur
        ).order_by('horodatage')
    else:
        transporteur = chauffeur
        messages = MessageClientChauffeur.objects.filter(
            transporteur=chauffeur
        ).order_by('horodatage')

    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            expediteur = role
            MessageClientChauffeur.objects.create(
                voyageur=voyageur if voyageur else request.POST.get('voyageur_id'),
                transporteur=transporteur,
                contenu=contenu,
                expediteur=expediteur
            )
            return redirect('tchat', transporteur_id=transporteur.id)

    context = {
        'messages': messages,
        'transporteur': transporteur,
        'role': role,
        'voyageur': voyageur,
    }
    return render(request, 'chat.html', context)


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
            code = str(random.randint(100000, 999999))
            VerificationCode.objects.update_or_create(
                user=user,
                defaults={'code': code}
            )
            request.session['pre_auth_user'] = user.id
            return redirect('verify_code')
    return render(request, 'user_app/usr_login.html')

def verify_code(request):
    user_id = request.session.get('pre_auth_user')
    if request.method == 'POST':
        code = request.POST['code']
        if VerificationCode.objects.filter(user_id=user_id, code=code).exists():
            user = VerificationCode.objects.get(user_iduser_id=user_id).user
            login(request, user)
            return redirect('dashboard')
    return render(request, 'user_app/usr_verify_code.html')


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
            VerificationCode.objects.update_or_create(
                user_iduser=user,
                defaults={'code': code}
            )
            request.session['pre_auth_chauffeur'] = user.id
            return redirect('chauffeur_app/verify_chauffeur')
    return render(request, 'chauffeur_app/cha_login.html')

def verify_chauffeur(request):
    user_id = request.session.get('pre_auth_chauffeur')
    if request.method == 'POST':
        code = request.POST['code']
        if VerificationCode.objects.filter(user_iduser_id=user_id, code=code).exists():
            user = VerificationCode.objects.get(user_iduser_id=user_id).user
            login(request, user)
            return redirect('dashboard_chauffeur')
    return render(request, 'chauffeur_app/cha_verify_code.html')


# ==========================
# 📊 Dashboards
# ==========================

@login_required
def dashboard(request):
    travels = Voyages.objects.filter(transporteurs__user=request.user)
    total = sum(v.prix_unitaire for v in travels)
    return render(request, 'user_app/usr_dashboard.html', {
        'user': request.user,
        'travel_count': travels.count(),
        'total_spent': total
    })

@login_required
def dashboard_chauffeur(request):
    travels = Voyages.objects.filter(transporteurs__user=request.user)
    total = sum(v.prix_unitaire for v in travels)
    return render(request, 'chauffeur_app/cha_dashboard.html', {
        'chauffeur': request.user,
        'travel_count': travels.count(),
        'total_earned': total
    })

@login_required
def tchat_vue(request, transporteur_id=None):
    user = request.user

    # Vérifie qui est connecté
    try:
        voyageur = Voyageurs.objects.get(user=user)
        role = 'voyageur'
    except Voyageurs.DoesNotExist:
        voyageur = None

    try:
        chauffeur = Transporteurs.objects.get(user=user)
        role = 'transporteur'
    except Transporteurs.DoesNotExist:
        chauffeur = None

    # Si client : il doit voir un chauffeur précis
    if role == 'voyageur':
        transporteur = get_object_or_404(Transporteurs, id=transporteur_id)
        messages = MessageClientChauffeur.objects.filter(
            voyageur=voyageur,
            transporteur=transporteur
        ).order_by('horodatage')
    else:
        transporteur = chauffeur
        messages = MessageClientChauffeur.objects.filter(
            transporteur=chauffeur
        ).order_by('horodatage')

    # Traitement envoi
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            expediteur = role
            message_obj = MessageClientChauffeur.objects.create(
                voyageur=voyageur if voyageur else request.POST.get('voyageur_id'),
                transporteur=transporteur,
                contenu=contenu,
                expediteur=expediteur
            )

            # ✅ Notification par e-mail
            if expediteur == 'voyageur':
                destinataire = transporteur.user.email
            else:
                destinataire = voyageur.user.email

            send_mail(
                subject="Nouveau message reçu",
                message=f"Vous avez reçu un message de {expediteur} :\\n\\n{message_obj.contenu}",
                from_email=None,
                recipient_list=[destinataire],
                fail_silently=True
            )
            return redirect('tchat', transporteur_id=transporteur.id)

    context = {
        'messages': messages,
        'transporteur': transporteur,
        'role': role,
        'voyageur': voyageur,
    }
    return render(request, 'user_app/chat_responsive.html', context)




def register_user(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        name = request.POST.get('name')
        firstname = request.POST.get('firstname')
        email = request.POST.get('email')

        if role == 'voyageur':
            Voyageurs.objects.create(
                name=name,
                firstname=firstname,
                email=email
            )
            messages.success(request, "Voyageur enregistré avec succès.")
        elif role == 'chauffeur':
            date_de_naissance = request.POST.get('date_de_naissance')
            adresse = request.POST.get('adresse')
            ville = request.POST.get('ville')
            permis = request.POST.get('permis')
            phone = request.POST.get('phone')

            Transporteurs.objects.create(
                name=name,
                firstname=firstname,
                email=email,
                date_de_naissance=datetime.strptime(date_de_naissance, '%Y-%m-%d'),
                adresse=adresse,
                ville=ville,
                permis=permis,
                phone=phone
            )
            messages.success(request, "Chauffeur enregistré avec succès.")
        else:
            messages.error(request, "Rôle invalide.")

        return redirect('login_user')

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
            return redirect('login')  # ou autre nom d’URL
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

def indisponible(request):

    """
        cette fonction permet de erreur 404
    """
    return render(request, 'html/404.html')

def question(request):

    """
        la page de la foire aux questions
        qui réponds à la plus part des questions que
        se posent les users
    """

    return render(request, 'html/FAQ.html')

def contact(request):

    return render(request, 'html/contact.html')


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


