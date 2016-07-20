import unittest
import cv2


from twitch_screen_grabber.examples.overwatch import calculate_score, get_most_likely_heroes


class TestImageRecognition(unittest.TestCase):
    def setUp(self):
        self.small_image = cv2.imread('tests/images/genji_target.png', 0)
        self.big_image = cv2.imread('tests/images/genji_scan.png', 0)
        self.big_image_dark = cv2.imread('tests/images/genji_scan_dark.png', 0)
        self.big_image_mccree = cv2.imread('tests/images/mccree_scan.png', 0)

    def test_score(self):
        self.assertGreater(calculate_score(self.small_image, self.big_image), 15)
        self.assertGreater(calculate_score(self.small_image, self.big_image_dark), 15)
        self.assertLess(calculate_score(self.small_image, self.big_image_mccree), 5)

    def test_most_likely_heroes(self):
        big_image = get_most_likely_heroes(self.big_image)
        dark_image = get_most_likely_heroes(self.big_image_dark)
        mccree_big_image = get_most_likely_heroes(self.big_image_mccree)
        self.assertEqual(big_image[0]['hero'], 'genji')
        self.assertEqual(dark_image[0]['hero'], 'genji')
        self.assertEqual(mccree_big_image[0]['hero'], 'mccree')


if __name__ == '__main__':
    unittest.main()
