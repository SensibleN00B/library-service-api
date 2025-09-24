from django.core.management.base import BaseCommand, CommandParser

from notifications.services import _get_admin_chat_ids, _sync_send_messages


class Command(BaseCommand):
    help = "Send a test message to configured Telegram admin chat(s)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "text",
            nargs="?",
            default="Test message from library notifications",
            help="Text to send",
        )

    def handle(self, *args, **options):
        text: str = options["text"]
        admin_ids = _get_admin_chat_ids()
        if not admin_ids:
            self.stdout.write(
                self.style.WARNING(
                    "No TELEGRAM_ADMINS_CHAT_IDS configured. Nothing to send."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Sending to {len(admin_ids)} "
                f"chat(s): {', '.join(map(str, admin_ids))}"
            )
        )
        _sync_send_messages(admin_ids, text)
        self.stdout.write(self.style.SUCCESS("Done."))
