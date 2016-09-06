from __future__ import unicode_literals

from requests import Request, Session
from requests.exceptions import ConnectionError

from django.db import models

from microservices.constants import NOT_ACCEPTED_RESPONSE_STATUS_CODES


class AvailableServiceManager(models.Manager):
    def get_queryset(self):
        return super(AvailableServiceManager, self).get_queryset().filter(is_available=True)


class UnavailableServiceManager(models.Manager):
    def get_queryset(self):
        return super(UnavailableServiceManager, self).get_queryset().filter(is_available=False)


class UnknownServiceManager(models.Manager):
    def get_queryset(self):
        return super(UnknownServiceManager, self).get_queryset().filter(is_available=None)


class Service(models.Model):
    name = models.CharField(
        unique=True,
        editable=False,
        max_length=100,
        help_text="Name of the service."
    )

    host = models.URLField(
        unique=True,
        editable=False,
        help_text="URL of the service. Ex. https://auth.example.com"
    )

    is_available = models.NullBooleanField(
        default=None,
        editable=False,
        help_text="True if the service can be reached."
    )

    objects = models.Manager()
    available = AvailableServiceManager()
    unavailable = UnavailableServiceManager()
    unknown = UnknownServiceManager()

    class Meta:
        ordering = ['name', 'host']

    def __str__(self):  # pragma: no cover
        return '{name} ({host})'.format(name=self.name, host=self.host)

    def __unicode__(self):  # pragma: no cover
        return '{name} ({host})'.format(name=self.name, host=self.host)

    def update_availability(self):
        """
        Update the availability status of the service object.

        :return: availability status (None | True | False)
        """

        availability = None

        try:
            session = Session()
            request = Request('HEAD', self.host)

            prepared_request = session.prepare_request(request)
            response = session.send(prepared_request)

            if response.status_code in NOT_ACCEPTED_RESPONSE_STATUS_CODES:
                raise ConnectionError('The status code of the response was {status_code}'.format(
                    status_code=response.status_code)
                )

            availability = True

        except ConnectionError:
            availability = False

        finally:
            self.is_available = availability
            self.save()

        return availability

    def remote_call(self, method, api='', headers=None, cookies=None, data=None, request_kw=None, session_kw=None):
        """
        Do a remote call to the service.

        :param method: HTTP Method name. ex: GET
        :param api: API endpoint url. ex: login/
        :param cookies: Cookies
        :param data: Data which will be send. ex: In case of POST.
        :param headers: Extra HTTP Headers

        :param request_kw: Other keyword arguments which can be passed to the Requests' Request object. ex: auth
        :param session_kw: Other keyword arguments which can be passed to the Requests' Session object. ex: timeout

        :return: response from the service
        """

        if request_kw is None:
            request_kw = {}

        if session_kw is None:
            session_kw = {}

        session = Session()

        host = self.host if self.host[-1] != '/' else self.host[:-1]
        api_endpoint = api if api[0] != '/' else api[1:]

        url = '{host}/{api_endpoint}'.format(host=host, api_endpoint=api_endpoint)
        request = Request(method=method.upper(), url=url, data=data, **request_kw)
        prepared_request = session.prepare_request(request)

        if headers is not None:
            prepared_request.headers.update(headers)

        if data is not None:
            prepared_request.data = data

        if cookies is not None:
            session.cookies.update(cookies)

        response = session.send(request=prepared_request, **session_kw)

        return response
