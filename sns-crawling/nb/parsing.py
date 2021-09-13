from pyquery import PyQuery as pq

from common import util


def get_nb_image(post_url):
    image = ""
    page = pq(url=post_url)
    frame = page.find("#mainFrame")
    url = "https://blog.naver.com" + frame.attr("src")
    page = pq(url=url)
    images = page.find("img")
    for item in images:
        item = pq(item)
        if "postfiles" in item.attr("src"):
            image = item.attr("src")
            image = str(image).split("?")
            image = image[0] + "?type=w773"
            break

    return image
