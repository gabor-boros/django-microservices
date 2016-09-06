from django.core.management.base import BaseCommand
from microservices.apps import services


class Command(BaseCommand):
    help = 'Check and update the availability status of services'

    def handle(self, *args, **options):
        for service in services.order_by('name'):
            service.update_availability()
            self.stdout.write(self.style.SUCCESS('Successfully updated service "{name}"'.format(name=service.name)))
