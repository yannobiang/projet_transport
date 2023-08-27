from django.db import models

# Create your models here.

class Transporteurs(models.Model) :

    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    date_de_naissance = models.DateField()
    adresse = models.TextField()
    ville = models.CharField(max_length=30)
    permis = models.CharField(max_length=5, default = "")
    phone = models.CharField(max_length= 60)
    email = models.EmailField()

    class Meta :
        verbose_name = ("Transporteur")
        verbose_name_plural = ("Transporteurs")
        ordering = ["name","firstname"]
    def __str__(self) -> str:
        return self.name

class Voyageurs(models.Model) :

    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    email = models.EmailField()
    class Meta :
        verbose_name = ("Voyageur")
        verbose_name_plural = ("Voyageurs")
    def __str__(self) -> str:
        return self.name

class Asso_trans_voyageur(models.Model):
    voyageurs = models.ForeignKey(Voyageurs, on_delete=models.CASCADE)
    transporteurs = models.ForeignKey(Transporteurs, on_delete=models.CASCADE)


class Voyages(models.Model) :
    
    date_depart = models.DateTimeField()
    date_arrivee = models.DateTimeField()
    ville_depart = models.CharField(max_length=50)
    ville_arrivee = models.CharField(max_length=50)
    prix_unitaire = models.FloatField()
    transporteurs = models.ForeignKey(Transporteurs, on_delete=models.CASCADE)
    class Meta :
        verbose_name = ("Voyage")
        verbose_name_plural = ("Voyages")
    
class Compagnie(models.Model):

    name = models.CharField(max_length=50)
    siren = models.BigIntegerField()
    transporteurs = models.ForeignKey(Transporteurs, on_delete=models.CASCADE)

    class Meta :
        verbose_name = ("Compagnie")
        verbose_name_plural = ("Compagnies")
        
    def __str__(self) -> str:
        return self.name

class Transports(models.Model):
    marque = models.CharField(max_length=50)
    matricule = models.CharField(max_length=50, default="")
    nombre_de_place = models.IntegerField()
    voyages = models.ForeignKey(Voyages, on_delete=models.CASCADE)
    compagnie = models.ForeignKey(Compagnie, on_delete=models.CASCADE)
    class Meta :
        verbose_name = ("Transport")
        verbose_name_plural = ("Transports")  
    