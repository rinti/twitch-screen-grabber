import unittest
import mock
import requests
import requests_mock
import os

from twitch_screen_grabber.twitch import TwitchGrabber

session = requests.Session()
adapter = requests_mock.Adapter()
session.mount('mock', adapter)

auth_mock_json = dict(
    token='asdf',
    sig='qwer',
)

m3u8_playlist = """
#EXTM3U
#EXT-X-TWITCH-INFO:NODE="video-edge-8f9594.arn01",MANIFEST-NODE="video-edge-8f9594.arn01",SERVER-TIME="1469041145.29",USER-IP="0.0.0.0",SERVING-ID="b20566127017432ca8826d62e3ed94b2",CLUSTER="arn01",ABS="false",BROADCAST-ID="9877654",STREAM-TIME="17263.2945919",MANIFEST-CLUSTER="arn01"
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="chunked",NAME="Source",AUTOSELECT=YES,DEFAULT=YES
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=4751000,RESOLUTION=1280x720,CODECS="avc1.640020,mp4a.40.2",VIDEO="chunked"
http://loremipsum.net/chunked/stream
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="high",NAME="High",AUTOSELECT=YES,DEFAULT=YES
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1760000,RESOLUTION=1280x720,CODECS="avc1.66.31,mp4a.40.2",VIDEO="high"
http://loremipsum.net/hls-826de0/test/high/index-live.m3u8?token=id=123456,bid=9877654,exp=1469127545,node=video-edge-8f9594.arn01,nname=video-edge-8f9594.arn01,fmt=high&sig=a855d5289ff5052225d88a10fe1a373f76e64f1d
#EXT-X-MEDIA:TYPE=VIDEO,GROUP-ID="audio_only",NAME="Audio Only",AUTOSELECT=NO,DEFAULT=NO
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=128000,CODECS="mp4a.40.2",VIDEO="audio_only"
http://loremipsum.net/hls-826de0/test/audio_only/index-live.m3u8?token=id=123456,bid=9877654,exp=1469127545,node=video-edge-8f9594.arn01,nname=video-edge-8f9594.arn01,fmt=audio_only&sig=c785d448da70410c9d0d71a96acbfffbd08dab89
"""

adapter.register_uri(
    'GET', 'mock://api.twitch.tv/api/channels/test/access_token', json=auth_mock_json,
)
adapter.register_uri(
    'GET', 'mock://usher.twitch.tv/api/channel/hls/test.m3u8', text=m3u8_playlist,
)
adapter.register_uri(
    'GET', 'mock://loremipsum.net/chunked/stream', text='http://loremipsum.net/file.ts',
)


def mock_requests_get(url, params=None):
    print url
    if url == 'http://api.twitch.tv/api/channels/test/access_token':
        print "Auth received"
        return session.get('mock://api.twitch.tv/api/channels/test/access_token')
    elif url == 'http://usher.twitch.tv/api/channel/hls/test.m3u8':
        return session.get('mock://usher.twitch.tv/api/channel/hls/test.m3u8')


def mock_m3u8_load(value):
    class Mock:
        @property
        def segments(self):
            return [Mock()]

        @property
        def base_uri(self):
            return 'http://loremipsum.net/chunks'

        @property
        def uri(self):
            return '/some/chunk.ts'
    return Mock()


class TestAPI(unittest.TestCase):
    def test_file_gets_cleaned_up(self):
        with TwitchGrabber('test') as stream:
            self.assertTrue(os.path.isfile(stream.f.name))
        # Clean up after with-statement
        self.assertFalse(os.path.isfile(stream.f.name))

    @mock.patch('requests.get', mock_requests_get)
    def test_get_auth_data(self):
        with TwitchGrabber('test') as stream:
            data = stream._get_auth_data()
            self.assertEqual(data, auth_mock_json)

    @mock.patch('requests.get', mock_requests_get)
    def test_get_livestream_m3u8_file(self):
        with TwitchGrabber('test') as stream:
            m3u8 = stream._get_livestream_m3u8_content()
            self.assertEqual(m3u8, m3u8_playlist)

    @mock.patch('requests.get', mock_requests_get)
    def test_get_highest_quality_stream(self):
        with TwitchGrabber('test') as stream:
            url = stream.get_highest_quality_stream()
            self.assertEqual(url, 'http://loremipsum.net/chunked/stream')

    @mock.patch('m3u8.load', mock_m3u8_load)
    @mock.patch('requests.get', mock_requests_get)
    def test_get_latest_segment_file_url(self):
        with TwitchGrabber('test') as stream:
            url = stream.get_latest_segment_file_url()
            self.assertEqual(url, 'http://loremipsum.net/chunks/some/chunk.ts')

if __name__ == '__main__':
    unittest.main()
