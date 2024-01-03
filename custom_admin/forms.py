from django import forms
from django.core.validators import RegexValidator
from .models import TelegramUser


class TelegramUserForm(forms.ModelForm):
    phone_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone_number = forms.CharField(validators=[phone_number_validator])

    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'first_name', 'last_name', 'username', 'phone_number']
