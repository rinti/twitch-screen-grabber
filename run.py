import random
import requests
import m3u8
import cv2
import tempfile
import os
import sys


def get_auth_data(channel):
    url = 'http://api.twitch.tv/api/channels/{channel}/access_token'.format(channel=channel)
    data = requests.get(url).json()
    return data


def get_live_stream_url(channel):
    url = 'http://usher.twitch.tv/api/channel/hls/{channel}.m3u8'.format(channel=channel)
    data = get_auth_data(channel)
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

    return requests.get(url, params=params).text


def get_highest_quality_stream(m3u8_obj):
    return m3u8_obj.playlists[0].uri


def get_latest_segment_file_url(m3u8_obj):
    obj = m3u8_obj.segments[0]
    return obj.base_uri + obj.uri


def make_temporary_file(segment_url):
    f = tempfile.NamedTemporaryFile(delete=False)
    # Write the data into our temp file
    response = requests.get(segment_url, stream=True)
    for block in response.iter_content(1024):
        f.write(block)
    return f


def get_most_likely_heroes(image):
    heroes = [
        'genji', 'mccree', 'pharah', 'reaper', 'soldier76', 'tracer',
        'bastion', 'bastion_turret', 'hanzo', 'junkrat', 'mei', 'torbjorn', 'widowmaker',
        'dva', 'reinhardt', 'roadhog', 'lucio', 'mercy', 'symmetra', 'zenyatta',
    ]
    heroes = [
        {'hero': hero, 'score': calculate_score(cv2.imread('tests/images/{}_target.png'.format(hero)), image)}
        for hero
        in heroes
    ]
    return sorted(heroes, key=lambda x: x['score'], reverse=True)


def calculate_score(target, full_screen):
    # function taken from
    # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_feature_homography/py_feature_homography.html#feature-homography

    sift = cv2.SIFT()
    kp1, des1 = sift.detectAndCompute(target, None)
    kp2, des2 = sift.detectAndCompute(full_screen, None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    match_count = 0
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
          match_count += 1

    return match_count


if __name__ == '__main__':
    stream = sys.argv[1]
    livestream = m3u8.loads(get_live_stream_url(stream))
    high_quality = m3u8.load(get_highest_quality_stream(livestream))
    segment_url = get_latest_segment_file_url(high_quality)

    f = make_temporary_file(segment_url)
    vidcap = cv2.VideoCapture(f.name)

    success, image = vidcap.read()

    f.close()
    os.unlink(f.name)

    for hero in get_most_likely_heroes(image)[:10]:
        print hero['hero'], hero['score']
