from datetime import datetime, timedelta
from pyquery import PyQuery as pq

from conf import config
from common import util


def parsing(html):
    q = pq(html)

    # post date and link
    post_date = q.find(config.facebook_dom["time"])
    date_utime = post_date.parent().attr("data-utime")
    date = util.get_ig_post_date(date_utime)

    link = post_date.parent().parent()
    link_url = "https://facebook.com" + link.attr("href")

    # text
    texts = q.find("p")
    content = ""
    for text in texts:
        text = pq(text)
        content += text.text() + "\n"

    # photo
    images = q.find(config.facebook_dom["image"]).find("a")
    image_urls = []
    image_file = ""
    i = 0
    for image in images:
        image = pq(image)
        if image.attr("data-ploi") is not None:
            image_urls.append(image.attr("data-ploi"))
            if i == 0:
                image_file = util.upload_file(image.attr("data-ploi"), config.s3["bucket"], "facebook/images")
            i += 1

    # video
    videos = q.find(config.facebook_dom["video"])
    video_urls = []
    video_file = ""
    i = 0
    for video in videos:
        video = pq(video)
        video_urls.append(video.attr("src"))
        if i == 0:
            video_file = util.upload_file(video.attr("src"), config.s3["bucket"], "facebook/videos")
        i += 1

    if video_file != "":
        result_image = video_file
    else:
        result_image = image_file

    result = {
        # "post_date": date.strftime("%Y-%m-%d %H:%M"),
        "post_date": date,
        "content": content,
        "content_link": link_url,
        "image": result_image,
    }

    return result
