from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'first_name', 'last_name', 'username', 'phone_number')
