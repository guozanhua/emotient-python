import json
import unittest

import mock

from emotient.emotient_client import APIWrapper
from emotient.error import EmotientAPIError

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def mock_http_client():
    return mock.MagicMock()


class TestAPIWrapper(unittest.TestCase):

    def setUp(self):
        super(TestAPIWrapper, self).setUp()
        self.api_base = 'https://api.emotient.com'
        self.api_key = 'API_KEY'
        self.http_client = mock_http_client()
        self.api_version = '1'
        self.api = APIWrapper(self.api_key, self.http_client, self.api_base, self.api_version)

    def test_get_headers(self):
        result = self.api.get_headers(None)
        self.assertDictEqual(result, {'Authorization': self.api_key})

        result = self.api.get_headers({'my_header': 123})
        self.assertDictEqual(result, {'Authorization': self.api_key, 'my_header': 123})

    def test_json_request(self):
        url = 'media'
        data = {
            'd': 2
        }
        params = {
            'x': 1
        }

        json_content = {
            'value': 3,
            'value2': {
                'value3': None
            }
        }
        content = json.dumps(json_content)
        headers = {
            'content-type': 'application/json'
        }

        self.http_client.request.return_value = (content, 200, headers)
        resp = self.api.request('GET', url, timeout=11, data=data, params=params)
        self.assertDictEqual(resp, json_content)
        self.http_client.request.assert_called_once_with('GET', 'https://api.emotient.com/v1/media',
                                                         {'Authorization': self.api_key}, data=json.dumps(data),
                                                         files=None, params=params, timeout=11)

    def test_invalid_request(self):
        url = 'media'

        json_content = {
            'message': 'Incorrect authentication credentials.'
        }
        content = json.dumps(json_content)
        headers = {
            'content-type': 'application/json'
        }

        self.http_client.request.return_value = (content, 400, headers)
        self.assertRaises(EmotientAPIError, self.api.request, 'GET', url)

    def test_invalid_request_html(self):
        url = 'medias'
        content = '<html></html>'
        headers = {
            'content-type': 'text/html'
        }
        self.http_client.request.return_value = (content, 404, headers)
        self.assertRaises(EmotientAPIError, self.api.request, 'GET', url)

    def test_request_to_file(self):
        blocks = ['abc,123', 'def,345']
        self.http_client.streaming_request.return_value = lambda x: blocks

        fp = StringIO()
        self.api.request_to_file(fp, 'GET', 'url')

        output = fp.getvalue()
        self.assertEqual(output, ''.join(blocks))

        fp.close()
