from sys import platform
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

import logging
import boto3
import requests
import uuid
import emoji

from conf import config


def upload_file(url, bucket, path, object_name=None):
    if object_name is None:
        object_name = path + "/" + str(uuid.uuid4()) + ".png"

    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=config.s3["aws_access_key_id"],
        aws_secret_access_key=config.s3["aws_secret_access_key"],
    )
    try:
        f = requests.get(url, stream=True)
        s3_client.upload_fileobj(f.raw, bucket, object_name, ExtraArgs={'ContentType': 'image/png'})
    except ClientError as e:
        logging.error(e)
        return False

    return object_name


def get_os():
    if platform.startswith("linux"):
        return "Linux"
    elif platform.startswith("darwin"):
        return "mac"
    elif platform.startswith("win"):
        return "windows"
    elif platform.startswith("cygwin"):
        return "windows"
    else:
        return None


def get_ig_post_date(post_utc_time):
    date = datetime.utcfromtimestamp(int(post_utc_time))
    date = date + timedelta(hours=9)

    return date


def get_yt_post_date(post_time):
    return datetime.strptime(get_yt_post_string(post_time), "%Y-%m-%dT%H:%M:%S")


def get_yt_post_string(post_time):
    return post_time[0:-6]


def ec(text=""):
    print(text, flush=True)


def emoji_free_text(text):
    return emoji.get_emoji_regexp().sub(r'', str(text))


def empty_line_dash_filter(text):
    return text.replace("\n-", "\n")


def get_tags(text):
    temp = str(text).split("#")
    tags = []

    for item in temp[1:]:
        tags.append("#" + str(item).split(" ")[0])

    tags = "".join(tags) + "#"
    if tags == "#":
        tags = ""

    print(tags)
    return tags
