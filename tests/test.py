import unittest
import mock
import requests
import requests_mock

from twitch_screen_grabber.twitch import TwitchGrabber

session = requests.Session()
adapter = requests_mock.Adapter()
session.mount('mock', adapter)

auth_mock_json = dict(
    token='asdf',
    sig='qwer',
)

adapter.register_uri(
    'GET', 'mock://api.twitch.tv/api/channels/test/access_token', json=auth_mock_json,
)
adapter.register_uri(
    'GET', 'mock://usher.twitch.tv/api/channel/hls/test.m3u8', text='http://loremipsum',
)


class TestAPI(unittest.TestCase):

    @mock.patch(
        'run.requests.get',
        lambda _: session.get('mock://api.twitch.tv/api/channels/test/access_token'))
    def test_get_auth_data(self):
        with TwitchGrabber('test') as stream:
            data = stream.get_auth_data('test')
            self.assertEqual(data, auth_mock_json)


if __name__ == '__main__':
    unittest.main()
