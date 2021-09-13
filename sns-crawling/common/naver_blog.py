from urllib import request
import time
import requests

import atoma

from conf import config
from common import crawl
from common import db
from common import util
from nb import parsing


def start_crawling(advertiser_id=0):
    start_time = time.time()

    accounts = db.get_sns_urls(4, advertiser_id)

    i = 0
    for account in accounts:
        total_post = 0
        new_post = 0
        overlap_post = 0

        url = "http://blog.rss.naver.com/" + account["account_code"] + ".xml"
        util.ec("=====================================")
        util.ec("NB Start: " + account["account_name"])
        try:
            response = requests.get(url)
            feed = atoma.parse_rss_bytes(response.content)

            for post in feed.items:
                util.ec(post.title)
                date = post.pub_date
                image = parsing.get_nb_image(post.link)
                result_image = util.upload_file(
                    image,
                    config.s3["bucket"],
                    "naver_blog/images")
                data = {
                    "account_id": account["account_id"],
                    "post_date": date.strftime("%Y-%m-%d %H:%M:%S"),
                    "title": post.title,
                    "content": post.description,
                    "content_link": post.link,
                    "image": result_image,
                }

                result = db.insert_post(data)
                total_post += 1
                if result == "NEW":
                    new_post += 1
                elif result == "OVERLAP":
                    overlap_post += 1

        except Exception as e:
            util.ec("[NAVER BLOG LOADING ERROR]")
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

    util.ec("[NB TOTAL TIME: %s]" % (time.time() - start_time))
