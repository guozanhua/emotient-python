from functools import partial
import json
import math
import random
import re
import string

import six

from emotient import api_base, api_version

if six.PY2:
    from urlparse import urlparse, parse_qs
else:
    from urllib.parse import urlparse, parse_qs


class MockAPI(object):

    def __init__(self, responses):
        self.group_media = {}
        self.groups = {}
        self.media = {}

        base_url = '{}/v{}'.format(api_base, api_version)

        guid_regex = '([\w\-]+)'

        # Media endpoints
        media_id_regex = re.compile('{}/media/{}\Z'.format(base_url, guid_regex))
        media_analytics_regex = re.compile('{}/analytics/{}\Z'.format(base_url, guid_regex))
        media_aggregate_regex = re.compile('{}/analytics/{}/aggregate'.format(base_url, guid_regex))

        media_list_callback = partial(self.list_callback, self.media)
        media_retrieve_callback = partial(self.retrieve_callback, self.media, media_id_regex)
        media_update_callback = partial(self.update_callback, self.media, media_id_regex)
        media_delete_callback = partial(self.delete_callback, self.media, media_id_regex)

        media_analytics_callback = partial(self.csv_callback, 'analytics', media_analytics_regex)
        media_aggregate_callback = partial(self.csv_callback, 'aggregate', media_aggregate_regex)

        responses.add_callback(responses.GET, '{}/media'.format(base_url),
                               callback=media_list_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, media_id_regex, callback=media_retrieve_callback,
                               content_type='application/json')
        responses.add_callback(responses.PUT, media_id_regex, callback=media_update_callback,
                               content_type='application/json')
        responses.add_callback(responses.DELETE, media_id_regex, callback=media_delete_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, '{}/search'.format(base_url), callback=media_list_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, media_analytics_regex, callback=media_analytics_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, media_aggregate_regex, callback=media_aggregate_callback,
                               content_type='application/json')

        responses.add_callback(responses.POST, '{}/upload'.format(base_url), callback=self.upload_callback,
                               content_type='application/json')

        # Group endpoints
        group_id_regex = re.compile('{}/groups/{}\Z'.format(base_url, guid_regex))
        group_aggregate_regex = re.compile('{}/analytics/groups/{}/aggregate'.format(base_url, guid_regex))
        group_metadata_regex = re.compile('{}/analytics/groups/{}/metadata'.format(base_url, guid_regex))

        group_list_callback = partial(self.list_callback, self.groups)
        group_retrieve_callback = partial(self.retrieve_callback, self.groups, group_id_regex)
        group_delete_callback = partial(self.delete_callback, self.groups, group_id_regex)
        group_create_callback = partial(self.create_callback, self.groups)
        group_update_callback = partial(self.update_callback, self.groups, group_id_regex)
        group_media_callback = partial(self.list_callback, self.group_media)

        group_aggregate_callback = partial(self.csv_callback, 'aggregate_group', group_aggregate_regex)
        group_metadata_callback = partial(self.csv_callback, 'metadata_group', group_metadata_regex)

        responses.add_callback(responses.GET, '{}/groups'.format(base_url), callback=group_list_callback,
                               content_type='application/json')
        responses.add_callback(responses.POST, '{}/groups'.format(base_url), callback=group_create_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, group_id_regex, callback=group_retrieve_callback,
                               content_type='application/json')
        responses.add_callback(responses.PUT, group_id_regex, callback=group_update_callback,
                               content_type='application/json')
        responses.add_callback(responses.DELETE, group_id_regex, callback=group_delete_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, group_aggregate_regex, callback=group_aggregate_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, group_metadata_regex, callback=group_metadata_callback,
                               content_type='application/json')
        responses.add_callback(responses.GET, re.compile('{}/groups/{}/media'.format(base_url, guid_regex)),
                               callback=group_media_callback, content_type='application/json')
        responses.add_callback(responses.PUT, re.compile('{}/groups/{}/media'.format(base_url, guid_regex)),
                               callback=self.group_action_callback, content_type='application/json')
        responses.add_callback(responses.DELETE, re.compile('{}/groups/{}/media'.format(base_url, guid_regex)),
                               callback=self.group_action_callback, content_type='application/json')

    def get_id(self, id_regex, url):
        match = id_regex.match(url)
        if not match:
            return False
        return match.group(1)

    def list_callback(self, data_dict, request):
        data_list = list(data_dict.values())
        headers = {'Content-Type': 'application/json'}
        _, _, _, _, qs, _ = urlparse(request.url)
        qs_dict = parse_qs(qs)
        page = int(qs_dict['page'][0])
        per_page = int(qs_dict['per_page'][0])
        start = per_page * (page-1)

        try:
            items = data_list[start:start+per_page]
        except IndexError:
            resp = {'message': 'Page not found.'}
            return 404, headers, json.dumps(resp)

        resp = {
            'current_page': page,
            'per_page': per_page,
            'pages': math.ceil(len(data_list) / float(per_page)),
            'total': len(data_list),
            'items': items
        }

        return 200, headers, json.dumps(resp)

    def create_callback(self, data_dict, request):
        headers = {'Content-Type': 'application/json'}
        random_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        payload = json.loads(request.body)
        payload['id'] = random_id
        data_dict[random_id] = payload
        return 201, headers, json.dumps(payload)

    def retrieve_callback(self, data_dict, id_regex, request):
        obj_id = self.get_id(id_regex, request.url)
        headers = {'Content-Type': 'application/json'}

        if obj_id in data_dict:
            resp = data_dict[obj_id]
            return 200, headers, json.dumps(resp)
        else:
            return 404, headers, json.dumps({'message': 'Not found.'})

    def update_callback(self, data_dict, id_regex, request):
        obj_id = self.get_id(id_regex, request.url)
        headers = {'Content-Type': 'application/json'}

        if obj_id in data_dict:
            payload = json.loads(request.body)
            data_dict[obj_id].update(payload)
            resp = data_dict[obj_id]
            return 200, headers, json.dumps(resp)
        else:
            return 404, headers, json.dumps({'message': 'Not found.'})

    def delete_callback(self, data_dict, id_regex, request):
        obj_id = self.get_id(id_regex, request.url)
        headers = {'Content-Type': 'application/json'}

        if obj_id in data_dict:
            del data_dict[obj_id]
            return 204, headers, ''
        else:
            return 404, headers, json.dumps({'message': 'Not found.'})

    def csv_callback(self, endpoint_name, id_regex, request):
        obj_id = self.get_id(id_regex, request.url)
        headers = {'Content-Type': 'text/csv'}
        return 200, headers, '{},{}'.format(endpoint_name, obj_id)

    def group_action_callback(self, request):
        # Echo back same ids for adding / removing from groups
        headers = {'Content-Type': 'application/json'}
        return 200, headers, request.body

    def upload_callback(self, request):
        headers = {'Content-Type': 'application/json'}
        random_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        self.media[random_id] = {
            'created_at': '2014-10-20T17:37:45+00:00',
            'duration': 22,
            'filename': 'ref.avi',
            'id': random_id,
            'metadata': {},
            'status': 'Analyzing',
        }
        return 201, headers, json.dumps({'id': random_id})

    def reset(self):
        self.groups.clear()
        self.group_media.clear()
        self.media.clear()
