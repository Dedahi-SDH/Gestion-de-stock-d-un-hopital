from django.db import models

# --------- PRODUITS -----------
class Produits(models.Model):
    CATEGORIES = [
        ('MED', 'Matériel Médical'),
        ('CHIR', 'Matériel Chirurgical'),
        ('PHAR', 'Produit Pharmaceutique'),
        ('BIO', 'Produit Biologique'),
        ('EQP', 'Equippement Bureautique'),
        ('LAB', 'Matériel de Laboratoire'),
        ('HYG', 'Produits d’Hygiène'),
        ('AMB', 'Matériel Ambulatoire'),
        ('STK', 'Stock Général'),
        ('DNT', 'Matériel Dentaire'),
    ]
    nom = models.CharField(max_length=50)
    libelle = models.CharField(max_length=50)
    quantite = models.IntegerField(default=0)
    description = models.TextField()
    date_expirations = models.DateField()
    date_fin = models.DateField()
    date_debut = models.DateField()
    categorie = models.CharField(max_length=10, choices=CATEGORIES, default='PHAR')
    seuil = models.IntegerField(default=4)
    quantite_entre = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom

# --------- STOCKS -----------
class Stocks(models.Model):
    produit = models.OneToOneField(Produits, on_delete=models.CASCADE)
    nbr_produits = models.IntegerField()  # stock initial ou total
    quantite_sortie = models.IntegerField(default=0)
    quantite_entre = models.IntegerField(default=0)
    categorie = models.CharField(max_length=50)
    date_sortie = models.DateField(auto_now_add=True, null=True, blank=True)

    @property
    def quantite_actuelle(self):
        return self.produit.quantite - self.quantite_sortie

    def quantite_initial(self):
        return self.nbr_produits - self.quantite_entre

    def __str__(self):
        return f"Stock de {self.produit.nom}"

# --------- ENTRÉE PRODUITS -----------
class EntreProduits(models.Model):
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    quantite_entre = models.PositiveIntegerField(default=0)
    date_ajout = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.quantite}) - {self.date_ajout}"


class SortieProduits(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    quantite_sortie = models.PositiveIntegerField(default=0)
    date_sortie = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Sortie de {self.quantite_sortie} unités - {self.stock.produit.nom}"


class Commande(models.Model):
    date_commande = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.date_commande}"

class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.stock.produit.nom} - {self.quantite}"

