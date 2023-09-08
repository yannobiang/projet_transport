from Company.models import (Transporteurs, Voyageurs, Voyages, Compagnie, Transports)

class fillData():

    """ Cette classe permet de surcharger les données dans la BD
        Il n ' y a que Transporteurs que j'ai reussi à charger
        Le problème se pose au niveau des cles primaire contrainte.
        Les deux tables transporteurs et voyageurs ont ete
    """

    def __init__(self, nom, data, model):

        self.nom = nom
        self.data = data 
        self.model = model 
        

    def charge(self):
        if self.nom == "dataTransporteurs":

            for element in range(len(self.data["name"])):
                New = self.model.objects.create(
                    name = self.data["name"][element],
                    firstname = self.data["firstname"][element],
                    date_de_naissance = self.data["date_de_naissance"][element],
                    ville = self.data["ville"][element],
                    permis = self.data["permis"][element],
                    phone = self.data["phone"][element],
                    email = self.data["email"][element]
                )
                New.save()
        elif self.nom == "dataVoyageurs":
            for element in range(len(self.data["name"])):
                New = self.model.objects.create(
                    name = self.data["name"][element],
                    firstname = self.data["firstname"][element],
                    email = self.data["email"][element]
                )
                New.save()

        elif self.nom == "dataVoyages":
            porteurs = Transporteurs.objects.all()

            for element in range(len(self.data["ville_depart"])):
                New = self.model.objects.create(
                    date_depart = self.data["date_depart"][element],
                    date_arrivee = self.data["date_arrivee"][element],
                    ville_depart = self.data["ville_depart"][element],
                    ville_arrivee = self.data["ville_arrivee"][element],
                    prix_unitaire = self.data["prix_unitaire"][element],
                    transporteurs = porteurs[element]
                )
                New.save()
        elif self.nom == "dataTransports":
            voyagesFirst = Voyages.objects.all()
            compagnieFirst = Compagnie.objects.all()

            for element in range(len(self.data["marque"])):
                New = self.model.objects.create(
                    marque = self.data["marque"][element],
                    matricule = self.data["matricule"][element],
                    nombre_de_place = self.data["nombre_de_place"][element],
                    voyages = voyagesFirst[element+1],
                    compagnie = compagnieFirst[element+1]
                )
                New.save()

        elif self.nom == "dataCompagnie":
            porteurs = Transporteurs.objects.all()
            print(porteurs)
            for element in range(len(self.data["siren"])):
                New = self.model.objects.create(
                    name = self.data["name"][element],
                    siren = self.data["siren"][element],
                    transporteurs = porteurs[element+1]
                    
                )
                New.save()
        elif self.nom == "Asso_trans_voyageur":
            New = self.model.objects.create(
            voyageurs = Voyageurs.objects.all(),
            transporteurs = Transporteurs.objects.all()
            )
            New.save()