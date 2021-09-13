import unittest

from common import util
from nb import parsing


class Test(unittest.TestCase):

    def test_nb_image_parsing(self):
        url = "https://blog.naver.com/bufs_iphak/221707677568"
        expect = "https://postfiles.pstatic.net/MjAxOTExMTRfMTY1/MDAxNTczNzE0MzcyNTg1.c7GUMD20fgsTweSnA0pPPMHDoV3hEtZybECZCmx4dvwg.PE5sqvqu4Vtov58MCB_PCfbpzRBAhDnqa3SYT6_7lFYg.PNG.bufs_iphak/면접꿀팁뉴스_선아.png?type=w773"

        image = parsing.get_nb_image(url)

        self.assertEqual(expect, image)

    def test_get_yt_datetime(self):
        date = "2019-10-01T14:12:19+00:00"
        expect = "2019-10-01 14:12:19"

        result = util.get_yt_post_date(date)

        self.assertEqual(expect, result.strftime("%Y-%m-%d %H:%M:%S"))

    def test_get_yt_post_string(self):
        date = "2019-10-01T14:12:19+00:00"
        expect = "2019-10-01T14:12:19"

        result = util.get_yt_post_string(date)

        self.assertEqual(expect, result)


if __name__ == "__main__":
    unittest.main()
