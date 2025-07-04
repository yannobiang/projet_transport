import os
import sys
import django
import pandas as pd

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport.settings')
# django.setup()

from Company.models import Transporteurs, Voyageurs, Voyages, Compagnie, Transports, Asso_trans_voyageur

class FillData:
    print(">>>>>> bonne classe importee")
    def __init__(self, filepath, user=None):
        self.filepath = filepath
        self.user = user
        self.xlsx = pd.read_excel(self.filepath, sheet_name=None)


    def charge(self):
        self.load_transporteurs()
        self.load_voyageurs()
        self.load_compagnie()
        self.load_transports()
        self.load_asso_trans_voyageur()
        self.load_voyages()

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

        voyages = list(Voyages.objects.all())
        compagnies = list(Compagnie.objects.all())

        for i, row in df.iterrows():
            Transports.objects.create(
                marque=row["marque"],
                matricule=row["matricule"],
                nombre_de_place=row["nombre_de_place"],
                voyages=voyages[i % len(voyages)],
                compagnie=compagnies[i % len(compagnies)],
            )
        print(f"✅ {len(df)} transports importés.")

    def load_voyageurs(self):
        df = self.xlsx.get("dataVoyageurs")
        if df is not None:
            for _, row in df.iterrows():
                Voyageurs.objects.create(
                    name=row["name"],
                    firstname=row["firstname"],
                    email=row["email"]
                )
            print(f"✅ {len(df)} voyageurs importés.")

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
        if df is None:
            print("❌ Feuille 'dataTransporteurs' introuvable.")
            return
        
        for _, row in df.iterrows():
            Transporteurs.objects.create(
                name=row["name"],
                firstname=row["firstname"],
                date_de_naissance=row["date_de_naissance"],
                adresse=row["adresse"],
                ville=row["ville"],
                permis=row["permis"],
                phone=row["phone"],
                email=row["email"]
            )
        print(f"✅ {len(df)} transporteurs importés.")

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