from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from stock.models import  Produits, Stocks, EntreProduits, SortieProduits, Commande, CommandeItem
from authentification.models import Utilisateurs
from django.contrib import messages
from stock.forms import CommandeForm, CommandeItemForm
from django.contrib.auth.decorators import login_required, user_passes_test
import io
import os
from django.db.models import Q
import arabic_reshaper
from bidi.algorithm import get_display
import barcode
import base64
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import render
from PIL import Image
from reportlab.pdfgen import canvas
import openpyxl
from openpyxl.styles import Font
from openpyxl import Workbook
from django.forms import inlineformset_factory
from django.forms import modelformset_factory
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
import io
import os
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from django.views.decorators.cache import never_cache
import xlsxwriter
from reportlab.platypus import Image
import os
from django.conf import settings
# Create your views here.

def no_cache(view_func):
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return _wrapped_view

#verifier si l'utilisateur est user ou admin:
def is_user(user):
    return user.is_authenticated and user.role == 'User'

#verifier si l'utilisateur est user ou admin:
def is_admin_or_user(user):
    return user.is_authenticated and user.role in ['Admin', 'User']

#vue d'index:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def index(request):
    # Comptages par catégorie
    eq_nombre = Stocks.objects.filter(categorie='EQP').count()
    phar_nombre = Stocks.objects.filter(categorie='PHAR').count()
    chir_nombre = Stocks.objects.filter(categorie='CHIR').count()
    med_nombre = Stocks.objects.filter(categorie='MED').count()
    bio_nombre = Stocks.objects.filter(categorie='BIO').count()
    stocks = Stocks.objects.select_related('produit')
    query = request.GET.get('q')  # Récupérer la recherche
    if query:
        stocks = stocks.filter(
            Q(produit__nom__icontains=query) |
            Q(produit__categorie__icontains=query) |
            Q(produit__quantite_entre__icontains=query)
        )

    return render(request, 'users/index.html', {
        'stocks': stocks,
        'phar_nombre': phar_nombre,
        'eq_nombre': eq_nombre,
        'med_nombre': med_nombre,
        'chir_nombre': chir_nombre,
        'bio_nombre': bio_nombre,
        'query': query,
    })

#vue de creation du commande:
@login_required
@user_passes_test(is_admin_or_user)
def creer_commande(request):
    CommandeItemFormSet = modelformset_factory(
        CommandeItem,
        form=CommandeItemForm,
        extra=10,
        can_delete=False
    )

    if request.method == 'POST':
        formset = CommandeItemFormSet(request.POST, queryset=CommandeItem.objects.none())

        if formset.is_valid():
            commande = Commande.objects.create()
            for form in formset:
                if form.cleaned_data:  # Vérifie que le formulaire contient des données
                    stock = form.cleaned_data.get('stock')
                    quantite = form.cleaned_data.get('quantite')
                    # Vérifier que stock et quantité sont renseignés
                    if not stock or not quantite:
                        continue
                    #Condition : quantité demandée > quantité actuelle
                    if quantite > stock.quantite_actuelle:
                        messages.error(
                            request,
                            f"Quantité insuffisante pour {stock.produit.nom} "
                            f"(disponible : {stock.quantite_actuelle})"
                        )
                        return render(request, 'users/commande_multiple.html', {
                            'formset': formset
                        })
                    #Créer la ligne de commande
                    CommandeItem.objects.create(
                        commande=commande,
                        stock=stock,
                        quantite=quantite
                    )
                    #Créer la sortie correspondante
                    SortieProduits.objects.create(
                        stock=stock,
                        quantite_sortie=quantite
                    )
                    #Mettre à jour les valeurs du stock
                    stock.quantite_sortie += quantite
                    stock.save()
            messages.success(request, "Commande enregistrée avec succès.")
            return redirect('facture', id=commande.id)
        else:
            messages.error(request, "Une erreur au niveau du nom du produit au quantite demander!!")
    else:
        formset = CommandeItemFormSet(queryset=CommandeItem.objects.none())
    return render(request, 'users/commande_multiple.html', {
        'formset': formset
    })

#vue facture:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def gestion_facture(request, id):
    # Récupérer la commande
    commande = get_object_or_404(Commande, id=id)

    # Générer le code-barres avec le numéro de commande
    barcode_io = io.BytesIO()
    code = barcode.get('code128', str(commande.id), writer=ImageWriter())
    code.write(barcode_io)
    barcode_io.seek(0)
    barcode_base64 = base64.b64encode(barcode_io.read()).decode()

    # Construire la liste des produits commandés (via CommandeItem)
    produits = []
    for item in commande.items.all():
        stock = item.stock
        produit = stock.produit
        produits.append({
            'nom': produit.nom,
            'libelle': produit.libelle,
            'description': getattr(produit, 'description', ''),
            'quantite': item.quantite,
            'categorie': produit.categorie,
            'date_debut': getattr(produit, 'date_debut', ''),
            'date_fin': getattr(produit, 'date_fin', ''),
        })

    context = {
        'barcode_data': barcode_base64,
        'date_facture': commande.date_commande,
        'produits': produits,
        'commande': commande,
    }
    return render(request, 'users/facture.html', context)


#vue de visite:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def visiter(request, id):
    produit = get_object_or_404(Stocks, id=id)
    return render(request, 'users/visiter.html', {'stock':produit})


#vue pour les sorites:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def Sortie_stock(request):
    sortie = SortieProduits.objects.select_related('stock__produit')
    query = request.GET.get('q')
    if query:
        sortie = sortie.filter(
            Q(stock__produit__nom__icontains=query) |
            Q(stock__produit__categorie__icontains=query) |
            Q(quantite_sortie__icontains=query)
        )
    return render(request, 'users/sortie.html', {'sortie': sortie, 'query': query})
#vue exporter pdf:
# Enregistre la police Amiri (ajuste le chemin vers ton fichier TTF)
font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
pdfmetrics.registerFont(TTFont('Amiri', font_path))
def afficher_arabe(texte):
    reshaped = arabic_reshaper.reshape(texte)
    return get_display(reshaped)


#vue PDF:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def facture_pdf(request, id):
    commande = get_object_or_404(Commande, id=id)
    user = request.user

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=50)
    styles = getSampleStyleSheet()

    style_left = ParagraphStyle('left', parent=styles['Normal'], alignment=TA_LEFT)
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER)
    style_right = ParagraphStyle('right', parent=styles['Normal'], alignment=TA_RIGHT, fontName='Amiri')

    story = []

    # 🔷 Entête
    fr_text = Paragraph(
        "République Islamique de Mauritanie<br/>"
        "Ministère de la Santé<br/>"
        "Hôpital Inconnu<br/>"
        "Honneur - Fraternité - Justice",
        style_left
    )

    ar_text = Paragraph(
        f"{afficher_arabe('الجمهورية الإسلامية الموريتانية')}<br/>"
        f"{afficher_arabe('وزارة الصحة')}<br/>"
        f"{afficher_arabe('مستشفى مجهول')}<br/>"
        f"{afficher_arabe('شرف - أخاء - عدالة')}",
        style_right
    )

    # ✅ Chemin absolu vers l'image dans static
    image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'sante_logo.jpg')
    logo = Image(image_path, width=60, height=60)  # Ajuste la taille si besoin

    # Table header
    header_table = Table([[fr_text, logo, ar_text]], colWidths=[180, 80, 180])
    header_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))

    # 🔷 Titre facture
    story.append(Paragraph(f"<b>Facture n°{commande.id}</b>", style_center))
    story.append(Paragraph(f"Date : {commande.date_commande}", style_center))
    story.append(Spacer(1, 20))

    # 🔷 Produits commandés
    data = [["Produit", "Quantité", "Catégorie"]]
    for item in commande.items.all():
        produit = item.stock.produit
        data.append([
            produit.nom,
            str(item.quantite),
            str(produit.categorie)
        ])

    table = Table(data, colWidths=[200, 100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(table)
    story.append(Spacer(1, 40))

    # 🔷 Pied de page : nom de l'utilisateur et signature
    user_name = Paragraph(f"Préparé par : {user.first_name} {user.last_name}", style_left)
    signature = Paragraph("Signature", style_right)

    footer = Table([[user_name, signature]], colWidths=[250, 250])
    footer.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(footer)

    # 🔷 Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


#vue excel:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def facture_excel(request, id):
    commande = get_object_or_404(Commande, id=id)
    user = request.user
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Facture")
    # 🔵 Styles
    format_bold = workbook.add_format({'bold': True})
    format_right = workbook.add_format({'align': 'right'})
    format_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True})
    format_border = workbook.add_format({'border': 1})
    # 🔵 Lignes de l'en-tête (Français & Arabe)
    fr_lines = [
        "République Islamique de Mauritanie",
        "Ministère de la Santé",
        "Hôpital Inconnu",
        "Honneur - Fraternité - Justice"
    ]
    ar_lines = [
        "الجمهورية الإسلامية الموريتانية",
        "وزارة الصحة",
        "مستشفى مجهول",
        "شرف - أخاء - عدالة"
    ]
    # Écriture de l'en-tête : français à gauche (col A), arabe à droite (col F)
    for i in range(4):
        worksheet.write(i, 0, fr_lines[i], format_bold)  # Col A
        worksheet.write(i, 5, ar_lines[i], format_right)  # Col F

    worksheet.set_column('A:A', 35)
    worksheet.set_column('F:F', 35)

    # 🔵 Titre et date
    row = 6
    worksheet.merge_range(row, 0, row, 5, f"Facture n°{commande.id}", format_center)
    row += 1
    worksheet.merge_range(row, 0, row, 5, f"Date : {commande.date_commande}", format_center)

    row += 2

    # 🔵 En-tête du tableau
    headers = ["Produit", "Quantité", "Catégorie"]
    for col, header in enumerate(headers):
        worksheet.write(row, col, header, format_border)

    # 🔵 Produits commandés
    row += 1
    for item in commande.items.all():
        produit = item.stock.produit
        worksheet.write(row, 0, produit.nom, format_border)
        worksheet.write(row, 1, item.quantite, format_border)
        worksheet.write(row, 2, str(produit.categorie), format_border)
        row += 1

    row += 2

    # 🔵 Footer : préparé par, signature
    worksheet.write(row, 0, f"Préparé par : {user.first_name} {user.last_name}", format_bold)
    worksheet.write(row, 5, "Signature", format_right)

    # 🔵 Finaliser le fichier
    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=facture_{commande.id}.xlsx'
    return response

#profil:
@login_required
@user_passes_test(is_admin_or_user)
@never_cache
def profil(request):
    utilisateur = request.user
    return render(request, 'users/profil.html', {'utilisateur': utilisateur})