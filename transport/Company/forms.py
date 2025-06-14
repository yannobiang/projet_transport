from django import forms


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
    