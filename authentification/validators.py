from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def get_help_text(self):
        return _("Votre mot de passe ne doit pas être trop similaire à vos informations personnelles.")

class CustomMinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Le mot de passe doit contenir au moins %(min_length)d caractères."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("Le mot de passe doit contenir au moins %(min_length)d caractères.") % {'min_length': self.min_length}

class CustomCommonPasswordValidator(CommonPasswordValidator):
    def get_help_text(self):
        return _("Le mot de passe ne peut pas être un mot de passe trop courant.")

class CustomNumericPasswordValidator:
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Le mot de passe ne peut pas être composé uniquement de chiffres."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("Le mot de passe ne doit pas être uniquement numérique.")
