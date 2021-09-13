from pymysql import cursors, connect
from conf import config
from common import util


def get_sns_urls(sns_type, ad_id=0):
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)

    if ad_id == 0:
        sql = "SELECT * FROM advertiser AS a JOIN sns_account AS s ON a.ad_id = s.advertiser_id AND a.use_flag = 1 AND s.use_flag = 1 AND s.type_id = %(type)s ORDER BY a.ad_id ASC, s.account_id ASC"
        data = {
            "type": sns_type
        }
    else:
        sql = "SELECT * FROM advertiser AS a JOIN sns_account AS s ON a.ad_id = s.advertiser_id AND a.use_flag = 1 AND s.use_flag = 1 AND s.type_id = %(type)s AND ad_id = %(ad_id)s ORDER BY a.ad_id ASC, s.account_id ASC"
        data = {
            "type": sns_type,
            "ad_id": ad_id
        }
    result = None

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, data)
            result = cursor.fetchall()
    except Exception as e:
        util.ec("[DB ERROR: get sns urls]")
        util.ec(e)
    finally:
        conn.close()

    return result


def insert_post(data):
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)
    result = None

    tags = util.get_tags(data["content"])
    data["tags"] = tags

    if "title" in data:
        sql = "INSERT INTO sns_content(account_id, title, content, content_link, tags, image, post_date, reg_date) "
        sql += "VALUES(%(account_id)s, %(title)s, %(content)s, %(content_link)s, %(tags)s, %(image)s, %(post_date)s, ADDTIME(UTC_TIMESTAMP(), '09:00'))"
    else:
        sql = "INSERT INTO sns_content(account_id, content, content_link, tags, image, post_date, reg_date) "
        sql += "VALUES(%(account_id)s, %(content)s, %(content_link)s, %(tags)s, %(image)s, %(post_date)s, ADDTIME(UTC_TIMESTAMP(), '09:00'))"

    try:
        if check_duplicate_post(data["account_id"], data["post_date"], data["content"]):
            # util.ec("It's duplicated post.")
            result = "OVERLAP"
        else:
            if data["image"] != "":
                with conn.cursor() as cursor:
                    cursor.execute(sql, data)
                    cursor.execute("COMMIT")
                    # util.ec("It's new!")
                    result = "NEW"
    except Exception as e:
        util.ec("[DB ERROR: insert a post]")
        util.ec(e)
    finally:
        conn.close()

    return result


def check_duplicate_post(account_id, post_date, content):
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)

    # sql = "SELECT * FROM sns_content WHERE account_id = %(account_id)s AND post_date = %(post_date)s AND content = %(content)s"
    sql = "SELECT * FROM sns_content WHERE account_id = %(account_id)s AND post_date = %(post_date)s"

    result = True

    try:
        with conn.cursor() as cursor:
            # cursor.execute(sql, {"account_id": account_id, "post_date": post_date, "content": content})
            cursor.execute(sql, {"account_id": account_id, "post_date": post_date})
            result = cursor.fetchall()
            if len(result) > 0:
                result = True
            else:
                result = False
    except Exception as e:
        util.ec("[DB ERROR: check duplicate error]")
        util.ec(e)
    finally:
        conn.close()

    return result


def get_contents_to_transfer(advertiser_id):
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)

    sql = """
        SELECT
          *
        FROM
          advertiser AS a
          JOIN sns_account AS sa
            ON a.ad_id = sa.advertiser_id
          JOIN sns_content AS c
            ON sa.account_id = c.account_id
          LEFT JOIN sns_transfer AS t
            ON t.`ad_id` = a.`ad_id`
            AND t.`content_id` = c.`content_id`
        WHERE a.ad_id = %(advertiser_id)s AND a.`use_flag` = 1
          AND sa.`use_flag` = 1
          AND (
            t.`is_transfer` IS NULL
            OR t.`is_transfer` = 0
          )
        ORDER BY c.post_date
    """

    data = {
        "advertiser_id": advertiser_id,
    }

    result = None

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, data)
            result = cursor.fetchall()
    except Exception as e:
        util.ec("[DB ERROR: get contents to transfer]")
        util.ec(e)
    finally:
        conn.close()

    return result


def post_transfer_ck(conn: connect, table, domain, data):
    sns_type = ["SNS Type", "FB", "IG", "YT", "NB"]

    matching_data = {}
    matching_data["wr_notice"] = 0
    matching_data["wr_secret"] = 0
    matching_data["ca_name"] = data["account_name"]
    matching_data["wr_option"] = "html"
    matching_data["wr_subject"] = "square"
    matching_data["wr_link1"] = data["content_link"]
    matching_data["wr_password"] = "*D6D785A07F5E3CDABBE02B50DCC75D05E04EF1AD"
    matching_data["wr_name"] = data["account_name"]
    matching_data["wr_datetime"] = data["post_date"]
    matching_data["wr_last"] = data["post_date"]
    matching_data["wr_file"] = 0
    matching_data["wr_use_slideview"] = 0
    matching_data["wr_slide_size"] = 0
    matching_data["wr_slide_only"] = 0
    matching_data["wr_title"] = data["title"] if data["title"] is not None else ""
    matching_data["wr_content"] = util.empty_line_dash_filter(util.emoji_free_text(data["content"]))
    matching_data["wr_sub_contents"] = util.empty_line_dash_filter(util.emoji_free_text(data["content"]))
    matching_data["wr_sns_type"] = sns_type[data["type_id"]]
    if data["image"] != "" and data["image"] is not None:
        matching_data["wr_img_url"] = domain + data["image"]
    else:
        matching_data["wr_img_url"] = ""
    matching_data["wr_1"] = data["reg_date"]
    matching_data["wr_4"] = data["account_code"]

    sql = "INSERT INTO {table}(" \
          "wr_notice, wr_secret, " \
          "ca_name, wr_option, wr_subject, wr_content, " \
          "wr_link1, wr_password, wr_name, wr_datetime, " \
          "wr_last, wr_file, wr_use_slideview, " \
          "wr_slide_size, wr_slide_only, wr_title,  " \
          "wr_sub_contents, wr_sns_type, wr_img_url, wr_1, wr_4) " \
          "VALUES(" \
          "%(wr_notice)s, %(wr_secret)s, " \
          "%(ca_name)s, %(wr_option)s, %(wr_subject)s, %(wr_content)s, " \
          "%(wr_link1)s, %(wr_password)s, %(wr_name)s, %(wr_datetime)s, " \
          "%(wr_last)s, %(wr_file)s, %(wr_use_slideview)s, " \
          "%(wr_slide_size)s, %(wr_slide_only)s, %(wr_title)s, " \
          "%(wr_sub_contents)s, %(wr_sns_type)s, %(wr_img_url)s, %(wr_1)s, %(wr_4)s)"

    util.ec(table)
    sql = sql.format(table=table)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, matching_data)
            wr_id = cursor.lastrowid
            cursor.execute("COMMIT")

            sql = "UPDATE {table} SET wr_parent = %(wr_parent)s WHERE wr_id = %(wr_id)s"
            sql = sql.format(table=table)
            util.ec(wr_id)
            cursor.execute(sql, {"wr_parent": wr_id, "wr_id": wr_id})
            cursor.execute("COMMIT")

            complete_transfer(data["ad_id"], data["content_id"])

    except Exception as e:
        util.ec("[DB ERROR: post transfer]")
        util.ec(e)


def post_transfer(conn: connect, table, domain, data):
    sns_type = ["SNS Type", "FB", "IG", "YT", "NB"]

    matching_data = {}
    matching_data["wr_notice"] = 0
    matching_data["wr_secret"] = 0
    matching_data["ca_name"] = data["category2"]
    matching_data["wr_option"] = "html"
    matching_data["wr_subject"] = "square"
    matching_data["wr_link1"] = data["content_link"]
    matching_data["wr_password"] = "*D6D785A07F5E3CDABBE02B50DCC75D05E04EF1AD"
    matching_data["wr_name"] = data["account_name"]
    matching_data["wr_datetime"] = data["post_date"]
    matching_data["wr_last"] = data["post_date"]
    matching_data["wr_file"] = 0
    matching_data["wr_use_slideview"] = 0
    matching_data["wr_slide_size"] = 0
    matching_data["wr_slide_only"] = 0
    matching_data["wr_title"] = data["title"] if data["title"] is not None else ""
    matching_data["wr_content"] = util.empty_line_dash_filter(util.emoji_free_text(data["content"]))
    matching_data["wr_sub_contents"] = util.empty_line_dash_filter(util.emoji_free_text(data["content"]))
    matching_data["wr_sns_type"] = sns_type[data["type_id"]]
    if data["image"] != "" and data["image"] is not None:
        matching_data["wr_img_url"] = domain + data["image"]
    else:
        matching_data["wr_img_url"] = ""
    matching_data["wr_1"] = data["reg_date"]
    matching_data["wr_4"] = data["account_code"]

    sql = "INSERT INTO {table}(" \
          "wr_notice, wr_secret, " \
          "ca_name, wr_option, wr_subject, wr_content, " \
          "wr_link1, wr_password, wr_name, wr_datetime, " \
          "wr_last, wr_file, wr_use_slideview, " \
          "wr_slide_size, wr_slide_only, wr_title,  " \
          "wr_sub_contents, wr_sns_type, wr_img_url, wr_1, wr_4) " \
          "VALUES(" \
          "%(wr_notice)s, %(wr_secret)s, " \
          "%(ca_name)s, %(wr_option)s, %(wr_subject)s, %(wr_content)s, " \
          "%(wr_link1)s, %(wr_password)s, %(wr_name)s, %(wr_datetime)s, " \
          "%(wr_last)s, %(wr_file)s, %(wr_use_slideview)s, " \
          "%(wr_slide_size)s, %(wr_slide_only)s, %(wr_title)s, " \
          "%(wr_sub_contents)s, %(wr_sns_type)s, %(wr_img_url)s, %(wr_1)s, %(wr_4)s)"

    util.ec(table)
    sql = sql.format(table=table)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, matching_data)
            wr_id = cursor.lastrowid
            cursor.execute("COMMIT")

            sql = "UPDATE {table} SET wr_parent = %(wr_parent)s WHERE wr_id = %(wr_id)s"
            sql = sql.format(table=table)
            util.ec(wr_id)
            cursor.execute(sql, {"wr_parent": wr_id, "wr_id": wr_id})
            cursor.execute("COMMIT")

            complete_transfer(data["ad_id"], data["content_id"])

    except Exception as e:
        util.ec("[DB ERROR: post transfer]")
        util.ec(e)


def complete_transfer(advertiser_id, content_id):
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)

    sql = "INSERT INTO sns_transfer(ad_id, content_id, is_transfer) " \
          "VALUES(%(advertiser_id)s, %(content_id)s, 1) " \
          "ON DUPLICATE KEY UPDATE is_transfer = 1"

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, {"advertiser_id": advertiser_id, "content_id": content_id})
            cursor.execute("COMMIT")
    except Exception as e:
        util.ec("[DB ERROR: complete transfer]")
        util.ec(e)
    finally:
        conn.close()


def get_advertisers():
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)

    sql = "SELECT * FROM advertiser WHERE use_flag = 1"

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
    except Exception as e:
        util.ec("[DB ERROR: complete transfer]")
        util.ec(e)
    finally:
        conn.close()

    return result


def get_sns_types():
    db_info = config.db
    conn = connect(host=db_info["host"],
                   user=db_info["user"],
                   password=db_info["password"],
                   db=db_info["db"],
                   charset=db_info["charset"],
                   cursorclass=cursors.DictCursor)

    sql = "SELECT * FROM sns_type WHERE use_flag = 1"

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
    except Exception as e:
        util.ec("[DB ERROR: complete transfer]")
        util.ec(e)
    finally:
        conn.close()

    return result
