from datetime import datetime
import unittest

from dateutil.tz import tzutc
import mock

from emotient import utils


class TestParseDts(unittest.TestCase):

    def test_parsing_dts(self):
        data = {
            object(): object(),
            'xy': 22,
            'x_at': 1,
            'created_at': '2014-10-20T17:37:45+00:00',
            'invalid_at': '2014-10-20T17:37:'
        }
        utils.parse_dts(data)
        self.assertEqual(data['xy'], 22)
        self.assertEqual(data['x_at'], 1)
        self.assertEqual(data['created_at'], datetime(2014, 10, 20, 17, 37, 45, tzinfo=tzutc()))
        self.assertEqual(data['invalid_at'], '2014-10-20T17:37:')


class TestGetIDs(unittest.TestCase):

    def test_id_str(self):
        media = '123'
        result = utils.get_ids(media)
        self.assertListEqual(result, [media])

    def test_media(self):
        media_id = 'abc'
        media = mock.MagicMock(spec=object, id=media_id)
        result = utils.get_ids(media)
        self.assertListEqual(result, [media_id])

    def test_iterable_ids(self):
        media = ['123', '221', '311']
        result = utils.get_ids(media)
        self.assertListEqual(result, media)

    def test_iterable_media(self):
        media_ids = ['abc', 'cdef', 'ghj']
        media = [mock.MagicMock(spec=object, id=media_id) for media_id in media_ids]
        result = utils.get_ids(media)
        self.assertListEqual(result, media_ids)
