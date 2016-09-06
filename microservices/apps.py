from __future__ import unicode_literals

import microservices

from django.apps import AppConfig

services = None


class MicroservicesConfig(AppConfig):
    name = 'microservices'

    def ready(self):
        from microservices.models import Service

        global services
        services = Service.objects.all()
