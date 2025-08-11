from django.urls import path
from . import views

urlpatterns = [
    #Connexion:
    path('deconnexion/', views.deconnexion, name="deconnexion"),
    path('', views.Inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),

]


