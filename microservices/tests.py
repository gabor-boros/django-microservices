import json
import os

import mock
import tempfile
import requests_mock

from StringIO import StringIO
from random import randint

from django.test import TestCase
from django.core.management import call_command

from microservices.models import Service
from microservices.helpers import refresh_service_configuration_data


def create_temp_file(content, suffix=".json"):
    suffix = '_%s%s' % (str(randint(100, 200)), suffix)
    _, file_path = tempfile.mkstemp(suffix=suffix)

    f = open(file_path, "w")
    f.write(content)
    f.close()

    return file_path


class ManagementCommandsTestCase(TestCase):
    def setUp(self):
        self.out = StringIO()
        self.host = 'mock://service1.com'

    @requests_mock.mock()
    def test_services_command(self, mock):
        mock.head(self.host, status_code=200)
        service1 = Service.objects.create(name="test1", host=self.host, is_available=True)

        args = []
        opts = {}

        call_command('check_services', stdout=self.out, *args, **opts)

        self.assertIn(
            'Successfully updated service "{service_name}"'.format(service_name=service1.name),
            self.out.getvalue()
        )

    def test_list_services_command_for_available(self):
        service1 = Service.objects.create(name="test1", host=self.host, is_available=True)

        args = []
        opts = {}

        call_command('list_services', stdout=self.out, *args, **opts)

        self.assertIn("{service_name} service is".format(service_name=service1.name), self.out.getvalue())
        self.assertIn("available", self.out.getvalue())

    def test_list_services_command_for_unavailable(self):
        service1 = Service.objects.create(name="test1", host=self.host, is_available=False)

        args = []
        opts = {}

        call_command('list_services', stdout=self.out, *args, **opts)

        self.assertIn("{service_name} service is".format(service_name=service1.name), self.out.getvalue())
        self.assertIn("unavailable", self.out.getvalue())

    def test_list_services_command_for_unknown(self):
        service1 = Service.objects.create(name="test1", host=self.host, is_available=None)

        args = []
        opts = {}

        call_command('list_services', stdout=self.out, *args, **opts)

        self.assertIn("{service_name} service is".format(service_name=service1.name), self.out.getvalue())
        self.assertIn("unknown", self.out.getvalue())


class HelpersTestCase(TestCase):
    def setUp(self):
        self.temp_file = create_temp_file
        self.configuration = [
            {
                "model": "microservices.service",
                "pk": 1,
                "fields": {
                    "name": "auth",
                    "host": "http://auth.com/",
                }
            }
        ]

    @requests_mock.mock()
    def test_get_config_from_url(self, mock):
        mock.get("mocked://microservice.io/service.json", status_code=200, json=self.configuration)
        refresh_service_configuration_data("mocked://microservice.io/service.json")

    def test_get_config_from_file(self):
        file_path = self.temp_file(json.dumps(self.configuration))
        refresh_service_configuration_data(file_path)

    def test_get_config_from_relative_path(self):
        file_path = os.path.relpath(self.temp_file(json.dumps(self.configuration)))
        refresh_service_configuration_data(file_path)


class ModelManagerTestCase(TestCase):
    def setUp(self):
        self.service1 = Service.objects.create(name="test1", host='mock://service1.com', is_available=None)
        self.service2 = Service.objects.create(name="test2", host='mock://service2.com', is_available=True)
        self.service3 = Service.objects.create(name="test3", host='mock://service3.com', is_available=False)

    def test_get_all_services(self):
        services = Service.objects.all()

        self.assertEqual(services.count(), 3)
        self.assertIn(self.service1, services)
        self.assertIn(self.service2, services)
        self.assertIn(self.service3, services)

    def test_get_unknown_services(self):
        unknown_services = Service.unknown.all()

        self.assertEqual(unknown_services.count(), 1)
        self.assertEqual(unknown_services.first(), self.service1)

    def test_get_available_services(self):
        available_services = Service.available.all()

        self.assertEqual(available_services.count(), 1)
        self.assertEqual(available_services.first(), self.service2)

    def test_get_unavailable_services(self):
        unavailable_services = Service.unavailable.all()

        self.assertEqual(unavailable_services.count(), 1)
        self.assertEqual(unavailable_services.first(), self.service3)


class APICallTestCase(TestCase):
    def setUp(self):
        self.host = "mocked://microservice.io"
        self.service = Service.objects.create(name="test", host=self.host)

    @requests_mock.mock()
    def test_update_service_is_available(self, mock):
        mock.head(self.host, status_code=200)
        is_available = self.service.update_availability()

        self.assertTrue(is_available)

    @requests_mock.mock()
    def test_update_service_is_unavailable(self, mock):
        mock.head(self.host, status_code=500)
        is_available = self.service.update_availability()

        self.assertFalse(is_available)

    @requests_mock.mock()
    def test_get(self, mock):
        mock.get('{0}/endpoint/'.format(self.host), status_code=200)
        response = self.service.remote_call(method='GET', api='endpoint/')

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_post(self, mock):
        post_data = {
            "name": "John Doe",
            "role": "Manager"
        }

        mock.post('{0}/endpoint/'.format(self.host), status_code=201, json=post_data)
        response = self.service.remote_call(method='POST', api='endpoint/', data=post_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content), post_data)

    @requests_mock.mock()
    def test_put(self, mock):
        put_data = {
            "role": "Manager"
        }

        response_data = {
            "name": "John Doe",
            "role": "Manager"
        }

        mock.put('{0}/endpoint/1/'.format(self.host), status_code=200, json=response_data)
        response = self.service.remote_call(method='PUT', api='endpoint/1/', data=put_data)

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(put_data, json.loads(response.content))

    @requests_mock.mock()
    def test_patch(self, mock):
        patch_data = {
            "role": "Manager"
        }

        response_data = {
            "name": "John Doe",
            "role": "Manager"
        }

        mock.patch('{0}/endpoint/1/'.format(self.host), status_code=200, json=response_data)
        response = self.service.remote_call(method='PATCH', api='endpoint/1/', data=patch_data)

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(patch_data, json.loads(response.content))

    @requests_mock.mock()
    def test_delete(self, mock):
        mock.delete('{0}/endpoint/1/'.format(self.host), status_code=204)
        response = self.service.remote_call(method='DELETE', api='endpoint/1/')

        self.assertEqual(response.status_code, 204)

    @requests_mock.mock()
    def test_headers(self, mock):
        header = {
            'ContentType': 'application/json'
        }

        mock.get('{0}/endpoint/'.format(self.host), status_code=200, headers=header)
        response = self.service.remote_call(method='GET', api='endpoint/', headers=header)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers, header)

    @requests_mock.mock()
    def test_cookies(self, mock):
        cookies = {
            'randomcookie': 'qwertzuiop'
        }

        mock.get('{0}/endpoint/'.format(self.host), status_code=200, cookies=cookies)
        response = self.service.remote_call(method='GET', api='endpoint/', cookies=cookies)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies, cookies)

    @requests_mock.mock()
    def test_request_kwargs(self, mock):
        header = {
            'ContentType': 'application/json'
        }

        mock.get('{0}/endpoint/'.format(self.host), status_code=200)
        response = self.service.remote_call(method='GET', api='endpoint/', request_kw={"headers": header})

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_session_kwargs(self, mock):
        mock.get('{0}/endpoint/'.format(self.host), status_code=200)
        response = self.service.remote_call(method='GET', api='endpoint/', session_kw={"timeout": 2000})

        self.assertEqual(response.status_code, 200)
