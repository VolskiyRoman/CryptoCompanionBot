from django.db import models

class TelegramUser(models.Model):
    telegram_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
