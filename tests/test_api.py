import copy
import unittest

import responses

from emotient.api import EmotientAnalyticsAPI
from emotient.utils import parse_dts
from tests.data.groups import GROUP_MEDIA, GROUPS
from tests.data.media import MEDIA
from tests.mock_api import MockAPI

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class APIClientTest(unittest.TestCase):

    def setUp(self):
        super(APIClientTest, self).setUp()
        self.rsps = responses.RequestsMock(assert_all_requests_are_fired=False)
        self.rsps.start()
        self.mock_api = MockAPI(self.rsps)
        self.api = EmotientAnalyticsAPI('API_KEY')

    def tearDown(self):
        super(APIClientTest, self).tearDown()
        self.rsps.stop()
        self.rsps.reset()

    def get_calls(self):
        return self.rsps._calls._calls


class TestAPIInit(unittest.TestCase):

    def test_custom_settings(self):

        class CustomHTTPClient(object):
            def __init__(self):
                self.requests = []

            def request(self, *args, **kwargs):
                self.requests.append((args, kwargs))
                return '{"id": "1"}', 200, {'content-type': 'application/json'}

        base = 'base'
        version = '33'
        http_client = CustomHTTPClient()
        client = EmotientAnalyticsAPI('API_KEY', http_client=http_client, api_base=base, api_version=version)
        client.media.retrieve('1')

        self.assertEqual(client.api_base, base)
        self.assertEqual(client.api_version, version)
        self.assertEqual(http_client.requests[0][0][1], u'base/v33/media/1')


class TestMedia(APIClientTest):

    def test_media_list(self):
        self.mock_api.media.update(MEDIA)
        media_list = list(self.api.media.list())

        for media in media_list:
            self.assertIn(media.data['id'], MEDIA)
        self.assertEqual(len(media_list), len(MEDIA))

        media_list = list(self.api.media.list(page=1, per_page=1))
        self.assertEqual(len(media_list), 1)

    def test_media_all(self):
        self.mock_api.media.update(MEDIA)

        total = 0
        for media in self.api.media.all(page=1, per_page=1):
            self.assertIn(media.data['id'], MEDIA)
            total += 1

        self.assertEqual(total, len(MEDIA))

    def test_media_retrieve(self):
        self.mock_api.media.update(MEDIA)
        mock_id = '19adeea0-88e0-d8fb-c899-864502a1011f'
        media = self.api.media.retrieve(mock_id)
        media_copy = copy.deepcopy(MEDIA[mock_id])
        parse_dts(media_copy)
        self.assertDictEqual(media_copy, media.data)

        self.mock_api.media[mock_id]['status'] = 'CHANGED'
        media.retrieve()
        self.assertEqual(media.data['status'], 'CHANGED')

    def test_media_update(self):
        self.mock_api.media.update(MEDIA)
        metadata = {
            'test': '123'
        }
        mock_id = '19adeea0-88e0-d8fb-c899-864502a1011f'
        media = self.api.media.update(mock_id, meta_data=metadata)
        self.assertDictEqual(media.data['meta_data'], metadata)

        metadata['x'] = 'y'
        media.update(meta_data=metadata)
        self.assertDictEqual(media.data['meta_data'], metadata)

    def test_media_delete(self):
        self.mock_api.media.update(MEDIA)
        mock_id = '19adeea0-88e0-d8fb-c899-864502a1011f'
        self.api.media.delete(mock_id)
        self.assertNotIn(mock_id, self.mock_api.media)

        mock_id2 = 'c9bffc11-bb98-a8c0-ca2e-49f20281011b'
        media = self.api.media.retrieve(mock_id2)
        media.delete()
        self.assertNotIn(mock_id2, self.mock_api.media)

    def test_media_upload(self):
        fp = StringIO()
        fp.write('test data')
        fp.seek(0)
        media = self.api.media.upload(fp)
        self.assertIn(media.id, self.mock_api.media)

    def test_search(self):
        self.mock_api.media.update(MEDIA)
        items = self.api.media.search('q')
        self.assertEqual(len(list(items)), 4)
        self.assertIn('https://api.emotient.com/v1/search', self.get_calls()[-1].request.url)

    def test_media_analytics(self):
        self.mock_api.media.update(MEDIA)
        mock_id = '19adeea0-88e0-d8fb-c899-864502a1011f'
        fp = StringIO()
        self.api.media.analytics(mock_id, fp)
        fp.seek(0)
        endpoint, obj_id = fp.read().split(',')
        self.assertEqual(endpoint, 'analytics')
        self.assertEqual(obj_id, mock_id)

        fp2 = StringIO()
        media = self.api.media.retrieve(mock_id)
        media.analytics(fp2)
        fp2.seek(0)
        endpoint, obj_id = fp2.read().split(',')
        self.assertEqual(endpoint, 'analytics')
        self.assertEqual(obj_id, mock_id)

    def test_media_aggregates(self):
        self.mock_api.media.update(MEDIA)
        mock_id = '19adeea0-88e0-d8fb-c899-864502a1011f'
        fp = StringIO()
        self.api.media.aggregated_analytics(mock_id, fp)
        fp.seek(0)
        endpoint, obj_id = fp.read().split(',')
        self.assertEqual(endpoint, 'aggregate')
        self.assertEqual(obj_id, mock_id)

        fp2 = StringIO()
        media = self.api.media.retrieve(mock_id)
        media.aggregated_analytics(fp2)
        fp2.seek(0)
        endpoint, obj_id = fp2.read().split(',')
        self.assertEqual(endpoint, 'aggregate')
        self.assertEqual(obj_id, mock_id)


class TestGroups(APIClientTest):

    def test_group_list(self):
        self.mock_api.groups.update(GROUPS)
        group_list = list(self.api.groups.list())

        for group in group_list:
            self.assertIn(group.data['id'], GROUPS)
        self.assertEqual(len(group_list), len(GROUPS))

        group_list = list(self.api.groups.list(page=1, per_page=1))
        self.assertEqual(len(group_list), 1)

    def test_group_create(self):
        data = {
            'name': 'GROUP11',
            'stimulus': None
        }
        group = self.api.groups.create(**data)
        self.assertIn(group.id, self.mock_api.groups)

    def test_group_retrieve(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        group = self.api.groups.retrieve(mock_id)
        self.assertEqual(GROUPS[mock_id]['id'], group.id)
        self.assertEqual(GROUPS[mock_id]['media_count'], group.data['media_count'])

        self.mock_api.groups[mock_id]['name'] = 'xyz'
        group.retrieve()
        self.assertEqual(group.data['name'], 'xyz')

    def test_group_update(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        name = '!!'
        group = self.api.groups.update(mock_id, name=name)
        self.assertEqual(group.data['name'], name)

        name2 = '@@!'
        group.update(name=name2)
        self.assertEqual(group.data['name'], name2)

    def test_group_delete(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        self.api.groups.delete(mock_id)
        self.assertNotIn(mock_id, self.mock_api.groups)

        mock_id2 = "4abe8d0b-2719-7268-e64d-beb004a102ca"
        group = self.api.groups.retrieve(mock_id2)
        group.delete()
        self.assertNotIn(mock_id2, self.mock_api.groups)

    def test_group_media_list(self):
        self.mock_api.groups.update(GROUPS)
        self.mock_api.group_media.update(GROUP_MEDIA)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        group = self.api.groups.retrieve(mock_id)
        media = list(group.media.list())
        self.assertEqual(len(media), len(GROUP_MEDIA))

    def test_add_to_group(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        group = self.api.groups.retrieve(mock_id)
        media_ids = ['id1', 'id2', 'id3']
        resp = group.media.add(media_ids)
        self.assertListEqual(media_ids, resp['ids'])

    def test_remove_from_group(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        group = self.api.groups.retrieve(mock_id)
        media_ids = ['id1', 'id2', 'id3']
        resp = group.media.remove(media_ids)
        self.assertListEqual(media_ids, resp['ids'])

    def test_group_aggregates(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        fp = StringIO()
        self.api.groups.aggregated_analytics(mock_id, fp)
        fp.seek(0)
        endpoint, obj_id = fp.read().split(',')
        self.assertEqual(endpoint, 'aggregate_group')
        self.assertEqual(obj_id, mock_id)

        fp2 = StringIO()
        group = self.api.groups.retrieve(mock_id)
        group.aggregated_analytics(fp2)
        fp2.seek(0)
        endpoint, obj_id = fp2.read().split(',')
        self.assertEqual(endpoint, 'aggregate_group')
        self.assertEqual(obj_id, mock_id)

    def test_group_metadata(self):
        self.mock_api.groups.update(GROUPS)
        mock_id = "3abe8d0b-2719-7268-e64d-beb004a102ca"
        fp = StringIO()
        self.api.groups.metadata(mock_id, fp)
        fp.seek(0)
        endpoint, obj_id = fp.read().split(',')
        self.assertEqual(endpoint, 'metadata_group')
        self.assertEqual(obj_id, mock_id)

        fp2 = StringIO()
        group = self.api.groups.retrieve(mock_id)
        group.metadata(fp2)
        fp2.seek(0)
        endpoint, obj_id = fp2.read().split(',')
        self.assertEqual(endpoint, 'metadata_group')
        self.assertEqual(obj_id, mock_id)
