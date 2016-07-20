import cv2


def get_most_likely_heroes(image):
    heroes = [
        {'hero': hero, 'score': calculate_score(cv2.imread('tests/images/{}_target.png'.format(hero)), image)}
        for hero
        in
        [
            'genji', 'mccree', 'pharah', 'reaper', 'soldier76', 'tracer',
            'bastion', 'bastion_turret', 'hanzo', 'junkrat', 'mei', 'torbjorn', 'widowmaker',
            'dva', 'reinhardt', 'roadhog', 'lucio', 'mercy', 'symmetra', 'zenyatta',
        ]
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

    return len(filter(lambda m: m[0].distance < 0.7 * m[1].distance, matches))


def get_most_likely_hero(stream):
    stream.get_latest_segment_file()

    vidcap = cv2.VideoCapture(stream.f.name)

    success, image = vidcap.read()
    h, w, _ = image.shape
    crop_h = h / 4
    crop_w = w / 2

    # image[y1:y2, x1:x2]
    image = image[h - crop_h:h, crop_w:w]
    # cv2.imwrite('debug.png', image)

    hero = get_most_likely_heroes(image)[0]
    if hero['score'] >= 9:
      print "Most likely: ", hero['hero']
    else:
      print "Couldn't make out which character \033[1m{}\033[0m was playing with enough confidence.".format(
          stream.channel
      )
