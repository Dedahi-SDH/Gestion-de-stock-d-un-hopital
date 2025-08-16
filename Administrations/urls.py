from django.urls import path
from . import views
urlpatterns = [
    #Produit pages:
    path('index_admin/', views.index_adminitrations, name="index_admin"),
    path('index_stock/', views.index_stock, name="index_stock"),
    path('entre_stock/', views.Entre_stock, name="entre_stock"),
    path('sortie_stock/', views.Sortie, name="Sortie_stock"),
    path('ajouter_produit/', views.Ajouter_produit, name="ajouter_produit"),
    path('modifier_produit/<int:id>/', views.Modifier_produit, name="modifier_produit"),
    path('supprimer_produit/<int:id>/', views.Confirmer_supprimer_produit, name="supprimer_produit"),
    path('visiter_produit/<int:id>/', views.Visiter_produit, name="visiter_produit"),
    path('ajouter_entrer/<int:id>/', views.ajouter_entree, name="ajouter_entrer"),
    #importations d'un fichier Excel:
    path('importation_Excel/', views.import_produits_stocks, name='importation_Excel'),
    path('reporting/', views.reporting_stock, name='reporting'),
    #Utilisateur pages:
    path('index_utilisateur/', views.index_utilisateur, name="index_utilisateur"),
    path('ajouter_utilisateur/', views.Ajouter_utilisateur, name="ajouter_utilisateur"),
    path('modifier_utilisateur/<int:id>/', views.Modifier_utilisateur, name="modifier_utilisateur"),
    path('supprimer_utilisateur/<int:id>/', views.Confirmer_supprimer_utilisateur, name="supprimer_utilisateur"),
    path('visiter_utilisateur/<int:id>/', views.Visiter_utilisateur, name="visiter_utilisateur"),
    path('statistique/', views.statistique, name="statistique"),
    path('retour_vers_admin/', views.retour_vers_admin, name="retour_vers_admin"),
    path('profil/', views.profil_admin, name="profil_admin"),
]
#
