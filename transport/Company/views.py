from django.shortcuts import render
from django.shortcuts import redirect
from datetime import date, datetime, timedelta, time, timezone
from django.utils.timezone import now, localdate, make_aware
from .models import Voyages
from .utils import convert
from django.core.serializers.json import DjangoJSONEncoder
import json

# Create your views here.


def home(request):

    """cette fonction lance la page home du site
        le result est une liste qui content autant de dictionnaire que de voyage
        chaque dictionnaire contient les informations sur le voyage
    """
    current = date.today().strftime("%Y-%m-%d")
    # récupération de la date actuelle
    today = now().date()
    start = datetime.combine(today - timedelta(days=1), time.min, tzinfo = timezone.utc)
    end = datetime.combine(today + timedelta(days=1), time.max, tzinfo = timezone.utc)
    
    # récupération de la date de demain
    
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    # filtrage des données
    # result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow)).filter(ville_depart__contains= 'LIBREVILLE').exclude(ville_arrivee='LIBREVILLE').values())
    
    # affichage des données
   

    if request.method == 'POST':
        dataSend = dict(request.POST)
        today =  datetime.strptime(dataSend['date_depart'][0], "%Y-%m-%d").date()

        if dataSend['trip'][0] == "aller":

            print("la date d'aujourd'hui :", today)
            yesterday = today - timedelta(days=1)
            print("la date d'hier :", yesterday)
            tomorrow = today + timedelta(days=1)
            print("la date de demain :", tomorrow)

            # filtrage des données
            list_of_depart = [col.upper() for col in dataSend['depart']]
            result = list(Voyages.objects.filter(date_depart__range=(yesterday, tomorrow))
                                         .filter(ville_depart__in=list_of_depart)
                                         .exclude(ville_arrivee__in=list_of_depart).values()
                        )
            for i in range(len(result)):
                
                result[i]['heures'] = convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[0]
                result[i]['minutes'] = convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[1]
                result[i]['second'] = convert(result[i]['date_arrivee'].timestamp() - result[i]['date_depart'].timestamp())[2]

            print("les données filtrées :", result)
            print(dataSend)
            context = { 'result' : result, 
                       "ville_depart" : dataSend['depart'][0],
                       "ville_arrivee" : dataSend['destination'][0],
                       "nombre_enfants" : dataSend['nbr_enf'][0], 
                       "nombre_adultes" : dataSend['nbr_adl'][0], 
                       "nombre_bagages" : dataSend['nbr_bga'][0]
                      }
            return render(request,'html/choix_du_voyage.html' , context = context)
    else:
        return render(request, 'html/section.html', context={
            'current': current,
            'tomorrow': tomorrow
        })




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


