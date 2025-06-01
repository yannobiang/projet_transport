
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
def convert(date):
    """
    Prend deux timestamps (en secondes) et renvoie une liste [heures, minutes, secondes]
    représentant la durée entre les deux.
    """
    heures = int(date // 3600)
    minutes = int((date % 3600) // 60)
    secondes = int(date % 60)
    return (heures, minutes, secondes)

def get_weekday(date_obj):
        """
        Renvoie le jour de la semaine pour une date donnée.
        """
        days = ["Lun", "Mar", "Merc", "Jeu", "Ven", "Sam", "Dima"]
        return days[date_obj.weekday()]

def get_month(date_obj):
    """
    Renvoie le nom du mois en français à partir d’un objet datetime.
    """
    mois = {
        '1':"janv", 
        "2":"fév", 
        "3":"mar", 
        "4" : "avr", 
        "5":"mai", 
        "6":"juin",
        "7":"juil", 
        "8":"août",
        "9": "sep", 
        "10": "oct", 
        "11":"nov", 
        "12":"déc"
    }
    return mois[str(date_obj)]

def safe_format_iso(date_str):
    try:
        if isinstance(date_str, str):
            return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except:
        pass
    return date_str  # retourne la valeur brute si invalider