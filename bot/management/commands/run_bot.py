import asyncio
import telebot
from django.core.management.base import BaseCommand
from bot.main_bot import bot


class Command(BaseCommand):
    help = "Running bot"

    def handle(self, *args, **options):
        try:
            asyncio.run(bot.infinity_polling())
        except Exception as err:
            telebot.logger.error(f"An error occurred while running the bot: {err}")
