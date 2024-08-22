# your_app/management/commands/runserver_with_celery.py

from django.core.management.base import BaseCommand
import subprocess
import sys

class Command(BaseCommand):
    help = 'Run the Django server and Celery worker'

    def handle(self, *args, **options):
        # Start the Celery worker
        celery_process = subprocess.Popen(['celery', '-A', 'web', 'worker', '--loglevel=info'])
        
        # Start the Django development server
        try:
            subprocess.run(['python', 'manage.py', 'runserver'])
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Shutting down Django server and Celery worker...'))
            celery_process.terminate()
            celery_process.wait()
            sys.exit(0)