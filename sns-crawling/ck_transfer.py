from pymysql import cursors, connect

from conf import config
from common import db, util

util.ec("Start transfer")

posts = db.get_contents_to_transfer(2)

util.ec("Count: %s" % len(posts))

db_info = config.db_transfer_ck
conn = connect(host=db_info["host"],
               user=db_info["user"],
               password=db_info["password"],
               db=db_info["db"],
               charset=db_info["charset"],
               cursorclass=cursors.DictCursor)

try:
    for post in posts:
        util.ec("A post")
        util.ec(post["category1"])
        db.post_transfer_ck(conn, db_info["table"], config.image_domain, post)
        util.ec()
except Exception as e:
    util.ec("[TRANSFER ERROR: transfer error]")
    util.ec(e)
finally:
    conn.close()

util.ec("Finish transfer")
