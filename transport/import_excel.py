import os
import sys
import django
import pandas as pd
from django.utils.crypto import get_random_string
from datetime import datetime
from tabulate import tabulate 

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport.settings')
# django.setup()

from Company.models import Transporteurs, Voyageurs, Voyages, Compagnie, Transports, Asso_trans_voyageur, CustomUser

class FillData:
    print(">>>>>> bonne classe importee")
    def __init__(self, filepath, user=None):
        self.filepath = filepath
        self.user = user
        self.xlsx = pd.read_excel(self.filepath, sheet_name=None)
        self.emails_existants = []  # 🆕 Ajout ici


    def charge(self):
        self.load_voyageurs()         # Nécessite CustomUser (voyageur)
        print("🚀 Début de l'importation des données transporteurs")
        self.load_transporteurs()     # Nécessite CustomUser (chauffeur)
        print("🚀 Début de l'importation des données compagnies")
        self.load_compagnie()         # Associe à un transporteur existant
        print("🚀 Début de l'importation des données voyages")
        self.load_transports()        # Dépend de voyages et compagnies
        print("🚀 Début de l'importation des données transports")
        self.load_voyages()           # Pas de dépendance critique
        print("🚀 Début de l'importation des données transports")
        self.load_asso_trans_voyageur()
        self.afficher_emails_existants()  

        # Ajout de l’historique après chargement
        from Company.models import HistoriqueImport
        feuilles = list(self.xlsx.keys())
        dimensions = {k: f"{v.shape[0]} lignes × {v.shape[1]} colonnes" for k, v in self.xlsx.items()}
        HistoriqueImport.objects.create(
            utilisateur=self.user,
            fichier=os.path.basename(self.filepath),
            feuilles_importees=", ".join(feuilles),
            dimensions=str(dimensions)
        )

    def load_transports(self):
        df = self.xlsx.get("dataTransports")
        if df is None:
            print("❌ Feuille 'dataTransports' introuvable dans le fichier.")
            return

        compagnies = list(Compagnie.objects.all())
        transporteurs = list(Transporteurs.objects.all())

        if not compagnies or not transporteurs:
            print("❌ Aucune compagnie ou transporteur trouvé pour associer les transports.")
            return

        for i, row in df.iterrows():
            Transports.objects.create(
                marque=row["marque"],
                matricule=row["matricule"],
                nombre_de_place=row["nombre_de_place"],
                compagnie=compagnies[i % len(compagnies)],
                transporteur=transporteurs[i % len(transporteurs)],
                places_disponibles=row["nombre_de_place"],
                bagages_disponibles=row.get("bagages_disponibles", 0),
                disponible=True
            )

        print(f"✅ {len(df)} transports importés.")

    def load_voyageurs(self):
        df = self.xlsx.get("dataVoyageurs")
        if df is not None:
            for _, row in df.iterrows():
                email = row["email"]
                if CustomUser.objects.filter(email=email).exists():
                    print(f"❌ Utilisateur déjà existant pour {email}, ignoré.")
                    self.emails_existants.append({
                        "type": "voyageur",
                        "email": email,
                        "nom": row["name"],
                        "prénom": row["firstname"]
                    })
                    continue
                
                password = get_random_string(10)
                user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        role="voyageur",
                        first_name=row["firstname"],
                        last_name=row["name"]
                    )

                Voyageurs.objects.create(
                        name=row["name"],
                        firstname=row["firstname"],
                        email=email,
                        user=user
                    )

            print(f"✅ {len(df)} voyageurs importés avec CustomUser.")

    def load_voyages(self):
        df = self.xlsx.get("dataVoyages")
        if df is None:
            print("❌ Feuille 'dataVoyages' introuvable dans le fichier.")
            return

        transporteurs = list(Transporteurs.objects.all())
        transports = list(Transports.objects.all())

        if not transporteurs or not transports:
            print("❌ Pas de transporteurs ou transports pour créer les voyages.")
            return

        for i, row in df.iterrows():
            Voyages.objects.create(
                date_depart=row["date_depart"],
                date_arrivee=row["date_arrivee"],
                ville_depart=row["ville_depart"],
                ville_arrivee=row["ville_arrivee"],
                prix_unitaire=row["prix_unitaire"],
                transporteurs=transporteurs[i % len(transporteurs)],
                transport=transports[i % len(transports)],  # ✅ maintenant correctement lié
            )

        print(f"✅ {len(df)} voyages importés.")
    
    def load_transporteurs(self):
        df = self.xlsx.get("dataTransporteurs")
        if df is not None:
            created = 0
            for _, row in df.iterrows():
                email = row["email"]

                # Vérifie si un transporteur avec ce mail existe déjà
                if Transporteurs.objects.filter(email=email).exists():
                    print(f"⚠️ Transporteur déjà existant pour {email}, ignoré.")
                    self.emails_existants.append({
                        "type": "transporteur",
                        "email": email,
                        "nom": row["name"],
                        "prénom": row["firstname"]
                    })
                    continue

                # Vérifie aussi que le CustomUser n’existe pas déjà
                if CustomUser.objects.filter(email=email).exists():
                    print(f"⚠️ Utilisateur déjà existant pour {email}, ignoré.")
                    self.emails_existants.append({
                        "type": "custom_user",
                        "email": email,
                        "nom": row["name"],
                        "prénom": row["firstname"]
                    })
                    continue

                
                    
                password = get_random_string(10)

                user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        role="chauffeur",
                        first_name=row["firstname"],
                        last_name=row["name"]
                    )

                Transporteurs.objects.create(
                        name=row["name"],
                        firstname=row["firstname"],
                        email=email,
                        phone=row["phone"],
                        ville=row["ville"],
                        permis=row["permis"],
                        adresse=row["adresse"],
                        date_de_naissance=pd.to_datetime(row["date_de_naissance"]).date(),
                        user=user
                    )

                created += 1

            print(f"✅ {created} transporteurs importés avec comptes CustomUser.")

    def afficher_emails_existants(self):
        if not self.emails_existants:
            print("✅ Aucun doublon d'email détecté.")
            return

        print("\n📌 Emails déjà existants ignorés :")
        tableau = [
            [e["type"], e["email"], e["nom"], e["prénom"]]
            for e in self.emails_existants
        ]
        print(tabulate(tableau, headers=["Type", "Email", "Nom", "Prénom"], tablefmt="grid"))

    def load_compagnie(self):
        df = self.xlsx.get("dataCompagnie")
        if df is not None:
            transporteurs = list(Transporteurs.objects.all())
            for i, row in df.iterrows():
                Compagnie.objects.create(
                    name=row["name"],
                    siren=row["siren"],
                    transporteurs=transporteurs[i % len(transporteurs)]
                )
            print(f"✅ {len(df)} compagnies importées.")

    def load_transports(self):
        df = self.xlsx.get("dataTransports")
        if df is None:
            print("❌ Feuille 'dataTransports' introuvable dans le fichier Excel.")
            return

        compagnies = list(Compagnie.objects.all())
        transporteurs = list(Transporteurs.objects.all())

        for i, row in df.iterrows():
           Transports.objects.create(
                marque=row["marque"],
                matricule=row["matricule"],
                nombre_de_place=row["nombre_de_place"],
                compagnie=compagnies[i % len(compagnies)],
                transporteur=transporteurs[i % len(transporteurs)],
                places_disponibles=row["nombre_de_place"],
                bagages_disponibles=row["bagages_disponibles"],
                disponible=True
            )
        print(f"✅ {len(df)} transports importés.")
    
    def load_asso_trans_voyageur(self):
        
        print("🧩 Association des voyageurs aux transports...")

        voyageurs = list(Voyageurs.objects.all())
        transports = list(Transporteurs.objects.all())

        if not voyageurs or not transports:
            print("❌ Aucun voyageur ou transport disponible pour l'association.")
            return

        nb_asso = min(len(voyageurs), len(transports))

        for i in range(nb_asso):
            Asso_trans_voyageur.objects.create(
                voyageurs=voyageurs[i],
                transporteurs=transports[i % len(transports)]  # cyclique si moins de transports
            )

        print(f"✅ {nb_asso} associations créées entre voyageurs et transports.")

# Point d'entrée
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Fichier Excel manquant")
    else:
        path = sys.argv[1]
        print(f"📥 Chargement depuis {path}")
        FillData(path).charge()
        print("✅ Import terminé avec succès.")