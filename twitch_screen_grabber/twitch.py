import random
import requests
import m3u8
import tempfile
import os


class TwitchGrabber(object):
    def __init__(self, channel):
        self.channel = channel
        self.f = tempfile.NamedTemporaryFile(delete=False)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.f:
          os.unlink(self.f.name)
          self.f.close()

    def _get_auth_data(self):
        url = 'http://api.twitch.tv/api/channels/{channel}/access_token'.format(channel=self.channel)
        data = requests.get(url).json()
        return data

    def _get_livestream_m3u8_content(self):
        url = 'http://usher.twitch.tv/api/channel/hls/{channel}.m3u8'.format(channel=self.channel)
        data = self._get_auth_data()
        token, sig = data['token'], data['sig']

        params = dict(
            token=token,
            sig=sig,
            allow_audio_only=True,
            allow_source=True,
            allow_spectre=False,
            type='any',
            p=random.randint(0, 99999)
        )
        content = requests.get(url, params=params).text
        return content

    def get_highest_quality_stream(self):
        return m3u8.loads(self._get_livestream_m3u8_content()).playlists[0].uri

    def get_latest_segment_file_url(self):
        stream = m3u8.load(self.get_highest_quality_stream())
        obj = stream.segments[0]
        return obj.base_uri + obj.uri

    def get_latest_segment_file(self):
        # Write the data into our temp file
        response = requests.get(
            self.get_latest_segment_file_url(),
            stream=True
        )
        for block in response.iter_content(1024):
            self.f.write(block)
        return self.f
