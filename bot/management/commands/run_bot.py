import asyncio
import logging
from django.core.management.base import BaseCommand
from bot.main_bot import bot
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Running bot"

    def handle(self, *args, **options):
        try:
            log_level = getattr(logging, settings.LOG_LEVEL.upper())
            logging.basicConfig(level=log_level)
            logger.info("Bot is starting...")
            asyncio.run(bot.infinity_polling())
        except Exception as err:
            logger.error(f"An error occurred while running the bot: {err}")
