from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Utilisateurs(AbstractUser):
    choix_role = [
        ('Admin', 'Administrateur'),
        ('User', 'utilisateur'),
    ]
    CATEGORIE = [
        ('MED', 'Médecin'),
        ('INF', 'Infirmier'),
        ('CHIR', 'Chirurgien'),
        ('ANS', 'Anesthésiste'),
        ('autres', 'Autres')
    ]
    role = models.CharField(max_length=50, choices=choix_role, default='Client')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    nni = models.BigIntegerField()
    num_phone = models.BigIntegerField()
    email = models.EmailField()
    adresse = models.CharField(max_length=20)
    num_poste = models.CharField(max_length=20)
    date_recrutement = models.DateField()
    date_naissance = models.DateField()
    categorie = models.CharField(max_length=20, choices=CATEGORIE, default='MED')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    poste = models.CharField(max_length=20, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name='utilisateur_groups',
        blank=True,
        verbose_name='groupes'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='utilisateur_permissions',
        blank=True,
        verbose_name='permissions utilisateur'
    )
