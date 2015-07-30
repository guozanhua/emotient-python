import unittest

from requests.exceptions import HTTPError, RequestException
import responses

from emotient.error import EmotientAPIError
from emotient.http_client import RequestsClient


class TestRequestsClient(unittest.TestCase):

    def setUp(self):
        super(TestRequestsClient, self).setUp()
        self.http_client = RequestsClient()

    @responses.activate
    def test_requests_failure(self):
        url = 'https://api.emotient.com'
        exc = HTTPError('Oops')
        responses.add(responses.GET, url, body=exc)
        self.assertRaises(EmotientAPIError, self.http_client.request, 'GET', url, {})

        url = 'https://api.emotient.com/v1/media'
        exc = RequestException('Oops')
        responses.add(responses.POST, url, body=exc)
        self.assertRaises(EmotientAPIError, self.http_client.request, 'POST', url, {})
