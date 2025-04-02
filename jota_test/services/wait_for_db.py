import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Waits for database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        max_retries = 20
        retry_delay = 5

        for i in range(max_retries):
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                self.stdout.write(f'Database unavailable, waiting {retry_delay} seconds... ({i+1}/{max_retries})')
                time.sleep(retry_delay)
        
        self.stdout.write(self.style.ERROR('Could not connect to database after retries'))
        exit(1)