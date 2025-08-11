from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateurs
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.validators import UnicodeUsernameValidator

class CustomUsernameValidator(UnicodeUsernameValidator):
    message = 'Caractères invalides dans le nom d\'utilisateur. Seuls les lettres, chiffres et @/./+/-/_ sont autorisés.'
class AuthForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[CustomUsernameValidator()],  # <-- Ajouter ici le validateur personnalisé
        error_messages={
            'required': "Le nom d'utilisateur est obligatoire.",
            'max_length': "Le nom d'utilisateur doit faire au maximum 150 caractères.",
            'invalid': "Caractères invalides dans le nom d'utilisateur.",
        },
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
    )
    class Meta:
        model = Utilisateurs
        fields = [
            'username', 'email', 'role', 'first_name',
            'num_phone', 'adresse', 'num_poste', 'poste', 'nni',
            'date_recrutement', 'date_naissance', 'categorie',
            'image',
            'password1', 'password2'
        ]

        labels = {
            'username': "Nom d'utilisateur",
            'email': "Adresse e-mail",
            'role': "Rôle",
            'first_name': "Prénom",
            'num_phone': "Téléphone",
            'adresse': "Adresse",
            'num_poste': "Numéro de poste",
            'poste': "Poste d'utilisateur",
            'NNI': "numero nationale d'identification",
            'date_recrutement': "Date de recrutement",
            'date_naissance': "Date de naissance",
            'categorie': "Catégorie",
            'image': "Image d'utilisateur",
            'password1': "Mot de passe",
            'password2': "Confirmation du mot de passe",
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse e-mail'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'num_phone': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse'}),
            'num_poste': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de poste'}),
            'poste': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'le poste d utilisateur'}),
            'date_recrutement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'}),
        }


class UpdateUserForm(UserChangeForm):
    password = None

    class Meta:
        model = Utilisateurs
        fields = [
            'username', 'email', 'role', 'first_name',
            'num_phone', 'adresse', 'num_poste', 'poste', 'nni',
            'date_recrutement', 'date_naissance', 'categorie', 'image'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'num_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'num_poste': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'date_recrutement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
