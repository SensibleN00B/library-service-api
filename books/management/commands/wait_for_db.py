import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Wait command to check if a database is ready."""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        is_connected = False
        delay = 3

        while not is_connected:
            try:
                connections["default"].ensure_connection()
                is_connected = True
            except OperationalError:
                self.stdout.write(
                    f"Database is not ready. Next try after {delay} seconds"
                )
                time.sleep(delay)

        self.stdout.write("Database is ready, let`l go!")
