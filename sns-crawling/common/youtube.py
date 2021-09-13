import time
import datetime

import feedparser

from conf import config
from common import db
from common import util


def start_crawling(advertiser_id=0):
    start_time = time.time()

    accounts = db.get_sns_urls(3, advertiser_id)

    i = 0
    for account in accounts:
        total_post = 0
        new_post = 0
        overlap_post = 0

        url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + account["account_code"]
        util.ec("=====================================")
        util.ec("YT Start: " + account["account_name"])
        try:
            feed = feedparser.parse(url)

            for post in feed.entries:
                date = util.get_yt_post_date(post.published)
                link = post.links[0].href
                image = post.media_thumbnail[0]["url"]
                result_image = util.upload_file(
                    image,
                    config.s3["bucket"],
                    "youtube/images")
                data = {
                    "account_id": account["account_id"],
                    "post_date": date.strftime("%Y-%m-%d %H:%M:%S"),
                    "title": post.title,
                    "content": post.description,
                    "content_link": link,
                    "image": result_image,
                }

                result = db.insert_post(data)
                total_post += 1
                if result == "NEW":
                    new_post += 1
                elif result == "OVERLAP":
                    overlap_post += 1

        except Exception as e:
            util.ec("[YOUTUBE LOADING ERROR]")
            util.ec(account["account_link"])
            util.ec(url)
            util.ec(e)

        util.ec("[NEW POST: %s]" % new_post)
        util.ec("[OVERLAP POST: %s]" % overlap_post)
        util.ec("[TOTAL POST: %s]" % total_post)

        util.ec("=====================================")

        i += 1
        # if i > 0:
        #     break

    util.ec("[YT TOTAL TIME: %s]" % (time.time() - start_time))
