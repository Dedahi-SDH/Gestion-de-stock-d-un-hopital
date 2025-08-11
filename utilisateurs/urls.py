from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('commande/<int:id>/', views.commande, name='lancer_commande'),
    path('facture/<int:id>/', views.gestion_facture, name='facture'),
    path('visiter/<int:id>/', views.visiter, name='visiter'),
    path('sortie/', views.Sortie_stock, name='sortie_stock'),
    # path('Excel/<int:id>/', views.export_excel, name='Excel'),
    # path('PDF/<int:id>/', views.export_pdf, name='PDF'),
    path('commande_multiple/', views.creer_commande, name='commande_multiple'),
    path('facture/pdf/<int:id>/', views.facture_pdf, name='facture_pdf'),
    path('facture/excel/<int:id>/', views.facture_excel, name='facture_excel'),
    path('profil/', views.profil, name='profil'),

]