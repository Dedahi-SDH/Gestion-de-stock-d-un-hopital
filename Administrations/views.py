from django.shortcuts import render, redirect, get_object_or_404
from stock.models import  Produits, Stocks, EntreProduits, SortieProduits
from django.contrib import messages
from .forms import AjoutProduitForm
from authentification.forms import UpdateUserForm
from authentification.forms import AuthForm
from authentification.models import Utilisateurs
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, Q
from django.db.models import Sum, Count
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from django.views.decorators.cache import never_cache

#verifier si l'utilisateur est admin:
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

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

#Listes des utilisateur(admin):
@login_required
@user_passes_test(is_admin)
@never_cache
def index_utilisateur(request):
    utilisateur = request.user

    # Compteurs par catégorie
    medecin = Utilisateurs.objects.filter(categorie="MED").count()
    infermier = Utilisateurs.objects.filter(categorie="INF").count()
    chirurgien = Utilisateurs.objects.filter(categorie="CHIR").count()
    anesthesie = Utilisateurs.objects.filter(categorie="ANS").count()

    query = request.GET.get('q')

    if query:
        utilisateurs = Utilisateurs.objects.filter(
            Q(first_name__icontains=query) |
            Q(username__icontains=query) |
            Q(nni__icontains=query) |
            Q(num_phone__icontains=query) |
            Q(poste__icontains=query)
        )
    else:
        utilisateurs = Utilisateurs.objects.all()

    return render(request, 'Admin/Utilisateurs/index_utilisateur.html', {
        'utilisateurs': utilisateurs,
        'medecin': medecin,
        'infermier': infermier,
        'anesthesie': anesthesie,
        'chirurgien': chirurgien,
        'utilisateur': utilisateur,
        'query': query,
    })

#L'ajout d'un utilisateur(est accesible pour l'admin):
@login_required
@user_passes_test(is_admin)
@never_cache
def Ajouter_utilisateur(request):
    if request.method == "POST":
        form = AuthForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur ajouté avec succès !')
            return redirect('index_admin')
        else:
            messages.error(request, "Erreur lors de l'ajout.")
    else:
        form = AuthForm()
    return render(request, 'Admin/Utilisateurs/ajouter_utilisateur.html', {'ajouter': form})#Modifier un utilisateur(Admin):

#La modification d'un utilisateur(est accesible pour l'admin):
@login_required
@user_passes_test(is_admin)
@never_cache
def Modifier_utilisateur(request, id):
    utilisateur = get_object_or_404(Utilisateurs, id=id)
    if request.method == "POST":
        form = UpdateUserForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur mis à jour avec succès')
            return redirect('index_admin')
        else:
            messages.error(request, 'Erreur lors de la mise à jour !')
    else:
        form = UpdateUserForm(instance=utilisateur)
    return render(request, 'Admin/Utilisateurs/modifier_utilisateur.html', {'form': form})

#suppression d'un utilisateur(Admin):
@login_required
@user_passes_test(is_admin)
@never_cache
def Confirmer_supprimer_utilisateur(request, id):
    utilisateur = get_object_or_404(Utilisateurs, id=id)
    if request.method == "POST":
        utilisateur.delete()
        messages.success(request, "utilisateur supprimé avec succès.")
        return redirect('index_utilisateur')
    return render(request, 'Admin/Utilisateurs/supprimer_utilisateur.html', {'utilisateur': utilisateur})

#visiter un utilisateur:
@login_required
@user_passes_test(is_admin)
@never_cache
def Visiter_utilisateur(request, id):
    utilisateur = get_object_or_404(Utilisateurs, id=id)
    return render(request, 'Admin/Utilisateurs/visiter_utilisateur.html', {'utilisateur':utilisateur})

#index_admin
@login_required
@user_passes_test(is_admin)
@never_cache
def index_adminitrations(request):
    utilisateur_connecte = request.user
    utilisateur = Utilisateurs.objects.filter(username=utilisateur_connecte.username).first()
    query = request.GET.get('q')
    # Recherche dans Stocks
    stocks = Stocks.objects.select_related('produit')
    if query:
        stocks = stocks.filter(
            Q(produit__nom__icontains=query) |
            Q(produit__categorie__icontains=query) |
            Q(produit__quantite_entre__icontains=query)
        )
    # Recherche dans Utilisateurs
    if query:
        utilisateurs = Utilisateurs.objects.filter(
            Q(first_name__icontains=query) |
            Q(username__icontains=query) |
            Q(nni__icontains=query) |
            Q(num_phone__icontains=query) |
            Q(poste__icontains=query)
        )
    else:
        utilisateurs = Utilisateurs.objects.all()
    # Compteurs
    utilisateur_count_user = Utilisateurs.objects.filter(role="User").count()
    utilisateur_count_admin = Utilisateurs.objects.filter(role="Admin").count()
    stock_count = stocks.count()
    # Alerte seuil bas
    seuil_bas = [
        stock for stock in stocks
        if stock.quantite_actuelle <= stock.produit.seuil or stock.quantite_actuelle == 0
    ]
    if seuil_bas:
        messages.warning(request, f"{len(seuil_bas)} produit(s) atteignent le seuil minimum ou sont en rupture !")
    return render(request, 'Admin/index_admin.html', {
        'stocks': stocks,
        'utilisateurs': utilisateurs,  # Envoi les utilisateurs filtrés ou tous
        'stock_count': stock_count,
        'seuil_bas': seuil_bas,
        'utilisateur': utilisateur,
        'utilisateur_count_user': utilisateur_count_user,
        'utilisateur_count_admin': utilisateur_count_admin,
        'query': query,
    })

#profil:
def profil_admin(request):
    utilisateur = request.user
    return render(request, 'Admin/profil.html', {'utilisateur': utilisateur})

#ajouter des produits:
@login_required
@user_passes_test(is_admin)
@never_cache
def Ajouter_produit(request):
    if request.method == "POST":
        ajouter = AjoutProduitForm(request.POST)
        if ajouter.is_valid():
            produit = ajouter.save()
            # Créer l'entrée de stock associée
            entre = EntreProduits.objects.create(
                produit=produit,
                quantite_entre=produit.quantite_entre,
                date_ajout=produit.date_debut
            )

            stock = Stocks.objects.create(
                produit=produit,
                nbr_produits=produit.quantite,
                quantite_entre=produit.quantite_entre,
                quantite_sortie=0,
                categorie=produit.categorie
            )
            messages.success(request, 'Produit et stock ajoutés avec succès !')
            return redirect('index_stock')
        else:
            messages.error(request, 'Erreur lors de l\'ajout du produit.')
    else:
        ajouter = AjoutProduitForm()
    return render(request, 'Admin/Produits/ajouter_produit.html', {'ajouter': ajouter})

#Ajouter une entre:
@login_required
@user_passes_test(is_admin)
@never_cache
def ajouter_entree(request, id):
    produit = get_object_or_404(Produits, id=id)
    if request.method == "POST":
        form = AjoutProduitForm(request.POST)
        if form.is_valid():
            quantite_ajoutee = form.cleaned_data['quantite']  # quantite saisie par l'admin

            # ✅ Mise à jour des quantités
            produit.quantite += quantite_ajoutee
            produit.quantite_entre += quantite_ajoutee
            produit.save()

            # ✅ Création de l’entrée (historique)
            EntreProduits.objects.create(
                produit=produit,
                quantite_entre=quantite_ajoutee,
                date_ajout=produit.date_debut
            )

            # ✅ Stock
            stock, created = Stocks.objects.get_or_create(
                produit=produit,
                defaults={
                    'nbr_produits': produit.quantite,
                    'quantite_entre': quantite_ajoutee,
                    'quantite_sortie': 0,
                    'categorie': produit.categorie
                }
            )
            if not created:
                stock.nbr_produits += quantite_ajoutee
                stock.quantite_entre += quantite_ajoutee
                stock.save()

            messages.success(request, "Entrée enregistrée avec succès.")
            return redirect('index_stock')
    else:
        form = AjoutProduitForm(initial={
            'nom': produit.nom,
            'libelle': produit.libelle,
            'description': produit.description,
            'date_expirations': produit.date_expirations,
            'date_fin': produit.date_fin,
            'date_debut': produit.date_debut,
            'categorie': produit.categorie,
            'date_ajout': produit.date_debut,
            'seuil': produit.seuil
        })

    return render(request, 'Admin/Produits/ajouter_entre.html', {'form': form, 'produit': produit})

#modifier des produits:
@login_required
@user_passes_test(is_admin)
@never_cache
def Modifier_produit(request, id):
    produit = get_object_or_404(Produits, id=id)
    if request.method == "POST":
        form = AjoutProduitForm(request.POST, instance=produit)
        form.fields.pop('quantite', None)
        form.fields.pop('seuil', None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit mis à jour avec succès')
            return redirect('index_stock')
        else:
            messages.error(request, 'Erreur lors de la mise à jour!')
    else:
        form = AjoutProduitForm(instance=produit)
        form.fields['quantite'].disabled = True
        form.fields['seuil'].disabled = True
    return render(request, 'Admin/Produits/modifier_produit.html', {'form': form})

#supprimer des produits:
@login_required
@user_passes_test(is_admin)
@never_cache
def Confirmer_supprimer_produit(request, id):
    produit = get_object_or_404(Produits, id=id)
    if request.method == "POST":
        produit.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect('index_stock')
    return render(request, 'Admin/Produits//supprimer_produit.html', {'produit': produit})

#visiter un produit:
@login_required
@user_passes_test(is_admin)
@never_cache
def Visiter_produit(request, id):
    produit = get_object_or_404(Produits, id=id)
    stock = Stocks.objects.filter(produit=produit).first()
    sorties = SortieProduits.objects.filter(stock__produit=produit)
    return render(request, 'Admin/Produits//visiter_produit.html',
                  {
                        'produit': produit,
                        'stock': stock,
                        'sorties': sorties
                  })

#index produit:
@login_required
@user_passes_test(is_admin)
@never_cache
def index_stock(request):
    stocks = Stocks.objects.all()
    produits = Produits.objects.all()
    utilisateurs = Utilisateurs.objects.all()
    utilisateur = request.user
    eq_nombre = Stocks.objects.filter(categorie='EQP').count()
    entrer = EntreProduits.objects.all()
    phar_nombre= Stocks.objects.filter(categorie= 'PHAR').count()
    chir_nombre= Stocks.objects.filter(categorie= 'CHIR').count()
    med_nombre= Stocks.objects.filter(categorie= 'MED').count()
    eq_nombre= Stocks.objects.filter(categorie= 'EQP').count()
    bio_nombre= Stocks.objects.filter(categorie= 'BIO').count()
    query = request.GET.get('q')
    # Recherche dans Stocks
    stocks = Stocks.objects.select_related('produit')
    if query:
        stocks = stocks.filter(
            Q(produit__nom__icontains=query) |
            Q(produit__categorie__icontains=query) |
            Q(produit__quantite_entre__icontains=query)
        )
    return render(request, 'Admin/Produits/index_stock.html', {
        'stocks': stocks,
        'produits':produits,
        'entrer':entrer,
        'phar_nombre':phar_nombre,
        'chir_nombre':chir_nombre,
        'med_nombre':med_nombre,
        'eq_nombre':eq_nombre,
        'bio_nombre':bio_nombre,
        'utilisateur':utilisateur,
        'utilisateurs':utilisateurs,
        'query':query
        })

#Gestion des entre:
@login_required
@user_passes_test(is_admin)
@never_cache
def Entre_stock(request):
    entre = EntreProduits.objects.all()
    utilisateurs = Utilisateurs.objects.all()
    utilisateur = request.user
    query = request.GET.get('q')
    # Recherche dans Stocks
    stocks = Stocks.objects.select_related('produit')
    if query:
        entre = entre.filter(
            Q(produit__nom__icontains=query) |
            Q(produit__categorie__icontains=query) |
            Q(produit__quantite_entre__icontains=query)
        )
    return render(request, 'Admin/Produits/entre_stock.html',
                  {
                      'entre':entre,
                      'utilisateur':utilisateur,
                      'utilisateurs':utilisateurs,
                      'query':query
                  })

#Pour l'utilisateur et l'admin
@login_required
@user_passes_test(is_admin)
@never_cache
def Sortie(request):
    sortie = SortieProduits.objects.select_related('stock__produit').all()
    utilisateurs = Utilisateurs.objects.all()
    utilisateur = request.user
    query = request.GET.get('q')
    if query:
        sortie = sortie.filter(
            Q(stock__produit__nom__icontains=query) |
            Q(stock__categorie__icontains=query) |
            Q(stock__quantite_entre__icontains=query)
        )

    return render(request, 'Admin/Produits/sortie_stock.html', {
        'utilisateurs': utilisateurs,
        'sortie': sortie,
        'utilisateur': utilisateur,
        'query': query,
    })

@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def parametre(request):
    return render(request, 'Admin/parametre.html')

@login_required
@user_passes_test(is_admin)
@never_cache
def statistique(request):
    utilisateurs = Utilisateurs.objects.all()
    utilisateur = request.user
    categories_qs = Stocks.objects.values_list('categorie', flat=True).distinct()
    categories = list(categories_qs)

    produits_data = []
    entrees_data = []
    sorties_data = []

    for cat in categories:
        produits = Stocks.objects.filter(categorie=cat).count()

        entrees = EntreProduits.objects.filter(produit__categorie=cat).aggregate(
            total=Sum('quantite_entre'))['total'] or 0

        sorties = SortieProduits.objects.filter(stock__categorie=cat).aggregate(
            total=Sum('quantite_sortie'))['total'] or 0

        produits_data.append(produits)
        entrees_data.append(entrees)
        sorties_data.append(sorties)

    context = {
        'categories': categories,
        'produits': produits_data,
        'entrees': entrees_data,
        'sorties': sorties_data,
        'utilisateur':utilisateur,
        'utilisateurs':utilisateurs,
    }

    return render(request, 'Admin/statistique.html', context)

@login_required
@user_passes_test(is_admin)
@never_cache
def retour_vers_admin(request):
    return redirect('index_admin')
