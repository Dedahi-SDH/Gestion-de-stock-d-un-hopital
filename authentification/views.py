from django.shortcuts import render, redirect
from django.contrib import messages
from authentification.forms import AuthForm
from authentification.models import Utilisateurs
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from django.views.decorators.cache import never_cache


def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

#verifier si l'utilisateur est user:
def is_user(user):
    return user.is_authenticated and user.role == 'User'

#verifier si l'utilisateur est user ou admin:
def is_admin_or_user(user):
    return user.is_authenticated and user.role in ['Admin', 'User']

def no_cache(view_func):
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return _wrapped_view

#Inscription:
@login_required
@user_passes_test(is_admin)
@never_cache
def Inscription(request):
    if request.method == "POST":
        form = AuthForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            return redirect('connexion')
    else:
        form = AuthForm()
    return render(request, 'auth/inscription.html', {'form': form})

# connexion Admin(pour l'admin et l'utilisateur):
@never_cache
def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Si c'est un administrateur
            if is_admin(user):
                return redirect('index_admin')
            elif is_user(user):
                return redirect('index')
            else:
                messages.error(request, "Accès refusé. Rôle non autorisé.")
                return redirect('connexion')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'auth/connexion.html')

#logout Admin:
@never_cache
def deconnexion(request):
    logout(request)
    return redirect('connexion')
