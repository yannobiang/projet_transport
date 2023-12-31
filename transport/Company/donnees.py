
from datetime import (tzinfo, timedelta, datetime, timezone)
import pytz

def addDateTimes(AAAA, MM, DD, HH, MN, SS=00):
    """ cette fonction permet de remplir le champs datetime dans la bdd """
    return datetime(year = AAAA, month = MM, day = DD, hour = HH, 
    minute = MN, second = SS, tzinfo=pytz.UTC)

dataTransporteurs = {
    "name" : ["Charly", "Chapart", "Martin", "Martial"],
    "firstname" :["Jean", "Pratick", "Chaperon", "Jean-Chalonçon"] ,
    "date_de_naissance" :["1994-02-28", "1989-10-30", "1988-05-05", "1994-03-14"] ,
    "ville" :["ST Dénis", "Oyem", "Port-Gentil", "Paris"] ,
    "permis" :["C", "B", "B", "D"] ,
    "phone" : ["02854732", "06854512", "01528496", "04528694"],
    "email" : ["charlyjean@popo.fr", "chapartpratick@popo.ga", "chaperonmartin@papa.fr", "martial.jean-chaloncon@aol.com"]
}

dataVoyageurs = {
    "name" : ["OBIANG", "MAPANGOU", "MOUNGUEGUI", "OYANE", "ANGUE"],
    "firstname" :["Yann", "Francis", "Candy", "Jose", "Marie-Claire"],
    "email" :["yannobiang@jiji.com", "francismapangou@popo.com", "candymounguegui@yahoo.fr", "joseoyane@gpail.com", "marieclaireangue@yahoo.fr"]
}

dataVoyages = {
    "date_depart" : [addDateTimes(2022, 8, 5, 14, 00), addDateTimes(2023, 9, 22, 12, 40), addDateTimes(2022, 5, 22, 16, 30),
    addDateTimes(2023, 3, 16, 2, 50), addDateTimes(2022, 6, 16, 10, 28), addDateTimes(2023, 1, 31, 23, 35)],
    "date_arrivee" : [addDateTimes(2022, 8, 5, 10, 00), addDateTimes(2023, 9, 12, 12, 40), addDateTimes(2022, 5, 30, 16, 30),
    addDateTimes(2023, 3, 15, 21, 15), addDateTimes(2022, 6, 15, 20, 38), addDateTimes(2023, 1, 31, 20, 25)],
    "ville_depart" : ["OYEM", "LIBREVILLE", "PORT-GENTIL", "FRANCEVILLE", "NTOUM"],
    "ville_arrivee" : ["LIBREVILLE", "PORT-GENTIL", "LIBREVILLE", "OYEM", "LIBREVILLE"],
    "prix_unitaire" :[7000, 20000, 20000, 50000, 1000]

}

dataTransports = {
    "marque" : ["4x4 Pajero", "Bus 4x4 Climatise", "Toyota Yaris", "Toyota Corolla", "Carina"],
    "matricule" : ["GALIB-125486", "GAOYE-258963", "GAFRA-147852", "GALIB-951753", "GALIB-357159", "GALIB-987123"], 
    "nombre_de_place" :[50, 30, 20, 4, 5, 50]
    
}

dataCompagnie = {
    "name" : ["Major", "Setrag", "Ndong Sima", "Major", "Ndong Sima", "Major", "GTM"],
    "siren" : ["123456", "456789", "654321", "987321", "951741", "258456", "985325"]
}
