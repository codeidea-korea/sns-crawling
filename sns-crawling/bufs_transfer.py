from pymysql import cursors, connect

from conf import config
from common import db, util

util.ec("Start transfer")

posts = db.get_contents_to_transfer(1)

util.ec("Count: %s" % len(posts))

db_info = config.db_transfer_bufsipsi
conn = connect(host=db_info["host"],
               user=db_info["user"],
               password=db_info["password"],
               db=db_info["db"],
               charset=db_info["charset"],
               cursorclass=cursors.DictCursor)

db_info2 = config.db_transfer_bufsipsi2
conn2 = connect(host=db_info2["host"],
                user=db_info2["user"],
                password=db_info2["password"],
                db=db_info2["db"],
                charset=db_info2["charset"],
                cursorclass=cursors.DictCursor)
try:
    for post in posts:
        util.ec("A post")
        util.ec(post["category3"])
        db.post_transfer(conn, db_info["table"], config.image_domain, post)
        db.post_transfer(conn2, db_info2["table"], config.image_domain, post)
        util.ec()
except Exception as e:
    util.ec("[TRANSFER ERROR: transfer error]")
    util.ec(e)
finally:
    conn.close()
    conn2.close()

util.ec("Finish transfer")
