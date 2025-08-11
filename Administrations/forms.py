from django import forms
from stock.models import Produits

class AjoutProduitForm(forms.ModelForm):
    class Meta:
        model = Produits
        fields = ['nom', 'libelle', 'quantite', 'description', 'date_expirations', 'date_fin', 'date_debut', 'categorie', 'seuil']
        labels = {
            'nom': 'Nom du produit',
            'libelle': 'Libellé',
            'quantite': 'Quantité',
            'quantite_entre': 'quantite entre',
            'description': 'Description',
            'date_expirations': 'Date d\'expiration',
            'date_fin': 'Date de fin d\'utilisation',
            'date_debut': 'Date de début d\'utilisation',
            'categorie': 'Catégorie du produit',
            'seuil': 'seuil'
        }
        widgets = {
            'date_expirations': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
        }


