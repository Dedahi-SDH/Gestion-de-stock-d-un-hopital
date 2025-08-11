from django import forms
from .models import Commande
from .models import CommandeItem
from django.forms import modelformset_factory


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = []  # ou ['date_commande'] si tu veux l'afficher (rarement)



class CommandeItemForm(forms.ModelForm):
    class Meta:
        model = CommandeItem
        fields = ['stock', 'quantite']
        widgets = {
            'stock': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control',
                'placeholder': 'Quantité à commander'
            }),
        }
        labels = {
            'stock': 'Produit',
            'quantite': 'Quantité',
        }

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite is not None and quantite <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à 0.")
        return quantite


