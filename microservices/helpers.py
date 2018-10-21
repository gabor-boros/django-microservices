import os
import tempfile
import requests

from django.core.management import call_command


def refresh_service_configuration_data(configuration_file):
    if not os.path.isfile(configuration_file):

        configuration = requests.get(configuration_file).content

        _, configuration_file = tempfile.mkstemp(suffix='.json')

        f = open(configuration_file, "wb+")
        f.write(configuration)
        f.close()

    call_command('loaddata', os.path.abspath(configuration_file))
