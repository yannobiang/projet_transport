from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time, timezone
from django.utils.timezone import now, localdate, make_aware
from .models import Voyages
from .utils import convert, get_weekday, get_month
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import get_template
from xhtml2pdf import pisa
from itertools import zip_longest
import json

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
            list_of_depart = [col.upper() for col in dataSend['depart']]
            result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow))
                                         .filter(ville_depart__in=list_of_depart)
                                         .exclude(ville_arrivee__in=list_of_depart).values()
                        )
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

            

            # filtrage des données
            list_of_depart = [col.upper() for col in dataSend['depart']]
            list_of_retour = [col.upper() for col in dataSend['destination']]
            result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow))
                                         .filter(ville_depart__in=list_of_depart)
                                         .exclude(ville_arrivee__in=list_of_depart).values()
                        )
            result_retour = list(Voyages.objects.filter(date_arrivee__gt= tomorrow)
                                         .filter(ville_depart__in=list_of_retour).values()
                        )
            # filtrage des données
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
        print("selected_index", selected_index)

        if selected_index is None:
            return HttpResponse("Erreur : aucun index sélectionné", status=400)
        try:
            index = int(selected_index)
        except ValueError:
            return HttpResponse("Erreur : index non valide", status=400)

        
        result_allers = json.loads(request.session.get("results_aller", "[]"))
        result_retours = json.loads(request.session.get("results_retour", "[]"))

        selected_aller = result_allers[index]
        selected_retour = result_retours[index] if index < len(result_retours) else {}

        request.session["selected_aller"] = json.dumps(selected_aller)
        request.session["selected_retour"] = json.dumps(selected_retour)

        return render(request, "html/infos_personnelles.html")

    return redirect('home')

def reservation(request):
    import json

    aller = json.loads(request.session.get("selected_aller", "{}"))
    retour = json.loads(request.session.get("selected_retour", "{}"))
    if request.method == "POST":    
        print("reservation POST request")
        aller["nom"] = request.POST.get("nom")
        aller["prenom"] = request.POST.get("prenom")
        aller["email"] = request.POST.get("email")
        aller["telephone"] = request.POST.get("telephone")
        aller["adresse"] = request.POST.get("adresse")

        retour["nom"] = request.POST.get("nom")
        retour["prenom"] = request.POST.get("prenom")
        retour["email"] = request.POST.get("email")
        retour["telephone"] = request.POST.get("telephone")
        retour["adresse"] = request.POST.get("adresse")

        # Enregistrement des informations dans la session
        request.session["nom"] = aller["nom"]
        request.session["prenom"] = aller["prenom"]
        request.session["email"] = aller["email"]
        request.session["telephone"] = aller["telephone"]
    # Formatage de la date dans aller
        if "date_depart" in aller:
            try:
                aller["date_depart"] = datetime.fromisoformat(aller["date_depart"]).strftime("%Y-%m-%d")
                aller["date_arrivee"] = datetime.fromisoformat(aller["date_arrivee"]).strftime("%Y-%m-%d")
            except ValueError:
                pass  # laisser tel quel si déjà formatée

        # Formatage de la date dans retour
        if "date_depart" in retour:
            try:
                retour["date_depart"] = datetime.fromisoformat(retour["date_depart"]).strftime("%Y-%m-%d")
                retour["date_arrivee"] = datetime.fromisoformat(retour["date_arrivee"]).strftime("%Y-%m-%d")
            except ValueError:
                pass

        infos = {
            "nom": request.session.get("nom"),
            "prenom": request.session.get("prenom"),
            "email": request.session.get("email"),
            "telephone": request.session.get("telephone"),
            "adresse": request.session.get("adresse"),
            "aller": aller,
            "retour": retour,
            "nombre_adultes": request.session.get("nombre_adultes"),
            "nombre_enfants": request.session.get("nombre_enfants"),
            "date_depart": request.session.get("date_depart"),
            "date_retour": request.session.get("date_retour"),
            "nombre_bagages": request.session.get("nombre_bagages"),
        }

        return render(request, "html/reservation.html", infos)
    return redirect('infos_personnelles')

def finaliser_reservation(request):

    print("finaliser_reservation called")
    if request.method == "POST":
        print("finaliser_reservation POST request")
        ville_depart = request.POST.get("ville_depart")
        ville_arrivee = request.POST.get("ville_arrivee")
        adultes = request.POST.get("adultes")
        enfants = request.POST.get("enfants")
        bagages = request.POST.get("bagages")
        date_depart = request.POST.get('date_depart')
        date_retour = request.POST.get('date_retour')

        # Vérification simple (tu peux améliorer ça)
        if not (ville_depart and ville_arrivee and date_depart and adultes):
            return HttpResponse("Informations manquantes", status=400)

        # Exemple de traitement : tu peux ici enregistrer en base
        reservation_details = {
            "ville_depart": ville_depart,
            "ville_arrivee": ville_arrivee,
            "date_depart": date_depart,
            "date_retour": date_retour,
            "adultes": adultes,
            "enfants": enfants,
            "bagages": bagages
        }
        # Enregistrement dans la session (ou base de données)
        print("finalisation details:", reservation_details)
        return render(request, "html/resume.html", {"reservation": reservation_details})

    return redirect("reservation")

def generate_pdf(request):
    context = {
        "titre": "Business Plan - Boulangerie au Gabon",
        "porteur": "Yann Martin OBIANG ENGUIE",
        "objectif": "Créer une boulangerie équipée avec des matériels importés de Chine, incluant un four et un groupe électrogène.",
        "equipements": [
            {"nom": "Four à pain", "prix": "2 000 €"},
            {"nom": "Groupe électrogène diesel", "prix": "3 500 €"},
            {"nom": "Pétrin", "prix": "1 000 €"},
        ],
        "financement": "Fonds propres + Demande de financement bancaire",
        "remarques": "Les équipements seront achetés en Chine, ce qui réduit les coûts d’environ 30%."
    }

    template = get_template("recapitulatif_pdf.html")
    html = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF")
    return response


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


