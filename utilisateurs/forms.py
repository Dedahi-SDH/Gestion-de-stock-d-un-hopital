from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateurs

class AuthForm(UserCreationForm):
    choix_role = [
        ('Admini', 'Administrateur'),
        ('Client', 'client'),
    ]
    role = forms.ChoiceField(choices=choix_role, label='Role')
    telephone = forms.CharField(label='Telephone')
    class Meta:
        model = Utilisateurs
        fields = ['username', 'password1', 'password2', 'role', 'telephone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur",
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mot de passe',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirmation du mot de passe',
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'telephone',
            }),
        }