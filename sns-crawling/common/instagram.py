import sys
from urllib import request
import requests
import time
import json

from conf import config
from common import crawl
from common import db
from common import util
from ig import crawling


def start_crawling(advertiser_id=0):
    start_time = time.time()

    accounts = db.get_sns_urls(2, advertiser_id)

    cookies = crawling.instgram_login()

    i = 0
    for account in accounts:
        all_post = 0
        total_post = 0
        new_post = 0
        overlap_post = 0

        url = "https://www.instagram.com/" + account["account_code"] + "/?__a=1"
        util.ec("=====================================")
        util.ec("IG Start: " + account["account_name"] + "/" + account["account_code"])
        try:
            # posts = requests.get(url).json()
            posts = requests.get(url, cookies=cookies).json()
            # with request.urlopen(url) as read:
            #     feeds_bytes = read.read()
            #     feeds = feeds_bytes.decode("utf8")
            #     posts = json.loads(feeds)

            posts = posts["graphql"]["user"]["edge_owner_to_timeline_media"]
            all_post = posts["count"]
            posts = posts["edges"]
            for post in posts:
                # print(json.dumps(post, sort_keys=True, indent=4))
                date = util.get_ig_post_date(post["node"]["taken_at_timestamp"])
                if len(post["node"]["edge_media_to_caption"]["edges"]) > 0:
                    content = post["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
                else:
                    content = ""
                link_url = "https://instagram.com/p/" + post["node"]["shortcode"]
                result_image = util.upload_file(
                    post["node"]["thumbnail_src"],
                    config.s3["bucket"],
                    "instagram/images")
                data = {
                    # "post_date": date.strftime("%Y-%m-%d %H:%M"),
                    "account_id": account["account_id"],
                    "post_date": date.strftime("%Y-%m-%d %H:%M"),
                    "content": content,
                    "content_link": link_url,
                    "image": result_image,
                }

                result = db.insert_post(data)
                total_post += 1
                if result == "NEW":
                    new_post += 1
                elif result == "OVERLAP":
                    overlap_post += 1

        except Exception as e:
            util.ec("[INSTAGRAM LOADING ERROR]")
            util.ec(account["account_link"])
            util.ec(url)
            util.ec(e)
            util.ec("Error on line {}".format(sys.exc_info()[-1].tb_lineno))

        util.ec("=====================================")

        i += 1
        # if i > 0:
        #     break

    util.ec("[IG TOTAL TIME: %s]" % (time.time() - start_time))
