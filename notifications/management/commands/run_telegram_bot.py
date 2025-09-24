from django.core.management.base import BaseCommand

from notifications.telegram_bot import run


class Command(BaseCommand):
    help = "Run Telegram bot long-polling (aiogram)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Telegram bot…"))
        run()

