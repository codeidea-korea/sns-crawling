import time

from conf import config
from common import crawl
from common import db
from common import util
from fb import crawling


def start_crawling(advertiser_id=0):
    start_time = time.time()

    accounts = db.get_sns_urls(1, advertiser_id)
    driver = crawl.get_driver()

    i = 0
    ad_id = accounts[0]["ad_id"]
    for account in accounts:
        all_post = 0
        total_post = 0
        new_post = 0
        overlap_post = 0
        if config.down_by_advertiser:
            if ad_id != account["ad_id"]:
                driver.quit()
                driver = crawl.get_driver()

        url = "https://www.facebook.com/pg/" + account["account_code"] + "/posts"
        util.ec("=====================================")
        util.ec("FB Start: " + account["account_name"])
        try:
            posts = crawling.get_page(driver, url)
            all_post = len(posts)
            for post in posts:
                post["account_id"] = account["account_id"]
                result = db.insert_post(post)
                total_post += 1
                if result == "NEW":
                    new_post += 1
                elif result == "OVERLAP":
                    overlap_post += 1

        except Exception as e:
            util.ec("[FACEBOOK LOADING ERROR]")
            util.ec(account["account_link"])
            util.ec(url)
            util.ec(e)

        util.ec("[NEW POST: %s]" % new_post)
        util.ec("[OVERLAP POST: %s]" % overlap_post)
        util.ec("[TOTAL POST: %s]" % total_post)
        util.ec("[ALL POST: %s]" % all_post)

        util.ec("=====================================")

        ad_id = account["ad_id"]

        i += 1
        # if i > 0:
        #     break

    driver.quit()

    util.ec("[FB TOTAL TIME: %s]" % (time.time() - start_time))
