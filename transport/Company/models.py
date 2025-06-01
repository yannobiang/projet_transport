from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.conf import settings

# ========================
# 🔐 Utilisateur personnalisé
# ========================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L’adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ========================
# 👤 Chauffeur
# ========================

class Transporteurs(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    date_de_naissance = models.DateField()
    adresse = models.TextField()
    ville = models.CharField(max_length=30)
    permis = models.CharField(max_length=5, default="")
    phone = models.CharField(max_length=60)
    email = models.EmailField()

    class Meta:
        verbose_name = "Transporteur"
        verbose_name_plural = "Transporteurs"
        ordering = ["name", "firstname"]

    def __str__(self):
        return self.name

# ========================
# 👤 Voyageur
# ========================

class Voyageurs(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    email = models.EmailField()

    class Meta:
        verbose_name = "Voyageur"
        verbose_name_plural = "Voyageurs"

    def __str__(self):
        return self.name

class MessageClientChauffeur(models.Model):
    voyageur = models.ForeignKey(Voyageurs, on_delete=models.CASCADE, related_name='messages_envoyes')
    transporteur = models.ForeignKey(Transporteurs, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField()
    horodatage = models.DateTimeField(auto_now_add=True)
    
    # champ pour savoir qui a envoyé (client ou chauffeur)
    EXPEDITEUR_CHOICES = [
        ('voyageur', 'Voyageur'),
        ('transporteur', 'Transporteur'),
    ]
    expediteur = models.CharField(max_length=20, choices=EXPEDITEUR_CHOICES)

    class Meta:
        ordering = ['-horodatage']

    def _str_(self):
        return f"{self.expediteur} -> {self.contenu[:30]}..."
# ========================
# 🔗 Association transporteurs/voyageurs
# ========================

class Asso_trans_voyageur(models.Model):
    voyageurs = models.ForeignKey(Voyageurs, on_delete=models.CASCADE)
    transporteurs = models.ForeignKey(Transporteurs, on_delete=models.CASCADE)

# ========================
# 🚌 Voyages
# ========================

class Voyages(models.Model):
    date_depart = models.DateTimeField()
    date_arrivee = models.DateTimeField()
    ville_depart = models.CharField(max_length=50)
    ville_arrivee = models.CharField(max_length=50)
    prix_unitaire = models.FloatField()
    transporteurs = models.ForeignKey(Transporteurs, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Voyage"
        verbose_name_plural = "Voyages"

# ========================
# 🏢 Compagnie
# ========================

class Compagnie(models.Model):
    name = models.CharField(max_length=50)
    siren = models.BigIntegerField()
    transporteurs = models.ForeignKey(Transporteurs, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Compagnie"
        verbose_name_plural = "Compagnies"

    def __str__(self):
        return self.name

# ========================
# 🚐 Transports
# ========================

class Transports(models.Model):
    marque = models.CharField(max_length=50)
    matricule = models.CharField(max_length=50, default="")
    nombre_de_place = models.IntegerField()
    voyages = models.ForeignKey(Voyages, on_delete=models.CASCADE)
    compagnie = models.ForeignKey(Compagnie, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Transport"
        verbose_name_plural = "Transports"
# ========================
# 🚐 Verification model
# ========================
class VerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Code {self.code} for {self.user.email}"