from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model

class ViderTableForm(forms.Form):
    modele = forms.ChoiceField(label="Choisir une table", choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtenir les modèles de l'app "Company"
        modele_choices = [
            (model._meta.label, model._meta.verbose_name_plural.title())
            for model in apps.get_app_config('Company').get_models()
        ]
        CustomUser = get_user_model()
        utilisateurs_normaux = CustomUser.objects.filter(is_staff=False, is_superuser=False)

        if utilisateurs_normaux.exists():
            modele_choices.append(
                (CustomUser._meta.label, "Utilisateurs (Voyageurs et Transporteurs)")
            )
        self.fields['modele'].choices = modele_choices

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Fichier Excel", 
        required=True
        )

class RowTripForm(forms.Form) : 

    """ cette classe est le modèle de formulaie"""
    CHOICES = [
        ('A', 'aller-simple'),
        ('AR', 'aller-retour'),
    ]
    
    sens_voyage = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect, 
        choices=CHOICES
        )

    ville_depart = forms.CharField(
        label = '',
    )

    ville_arrivee = forms.CharField(
        label='',
    )

    date_depart = forms.SelectDateWidget(
       
    )
    