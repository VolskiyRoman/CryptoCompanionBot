# Generated by Django 5.0.1 on 2024-01-02 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin', '0002_telegramuser_delete_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramuser',
            name='user',
        ),
    ]