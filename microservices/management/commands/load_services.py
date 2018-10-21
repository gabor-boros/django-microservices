from django.core.management.base import BaseCommand

from microservices.app_settings import SERVICE_CONFIGURATION_FILE
from microservices.helpers import refresh_service_configuration_data


class Command(BaseCommand):
    help = 'Load configuration of the services'

    def handle(self, *args, **options):
        self.stdout.write('Loading service configuration from {location}'.format(
            location=str(SERVICE_CONFIGURATION_FILE))
        )

        try:
            refresh_service_configuration_data(SERVICE_CONFIGURATION_FILE)
            self.stdout.write(self.style.SUCCESS('Configuration loaded successfully'))

        except Exception as exc:
            self.stderr.write(self.style.ERROR('Configuration can not be loaded.\n{exc}'.format(exc=exc)))
