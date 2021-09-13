from operator import itemgetter

from common import db


def get_advertisers():
    advertisers = db.get_advertisers()
    for item in advertisers:
        print(str(item["ad_id"]) + ": " + item["ad_name"])
    print()

    return advertisers


def get_sns_types():
    sns_types = db.get_sns_types()
    sns_types.append({"type_id": 5, "sns_name": "Facebook 제외 나머지 모두"})
    for item in sns_types:
        print(str(item["type_id"]) + ": " + item["sns_name"])
    print()

    return sns_types


# Advertiser
advertiser = None
loop = True
while loop:
    advertisers = get_advertisers()
    advertiser = input("광고주 번호를 입력하세요 : ")
    print()
    print()
    if advertiser.isnumeric() is False or int(advertiser) not in list(map(itemgetter("ad_id"), advertisers)):
        print("다시 선택해 주세요.")
        print()
    else:
        loop = False

# SNS Type
type_id = None
loop = True
while loop:
    sns_types = get_sns_types()
    type_id = input("진행할 SNS를 선택해 주세요 : ")
    print()
    print()
    if type_id.isnumeric() is False or int(type_id) not in list(map(itemgetter("type_id"), sns_types)):
        print("다시 선택해 주세요.")
        print()
    else:
        loop = False

if advertiser.isnumeric() and type_id.isnumeric():
    type_id = int(type_id)
    if type_id == 1:
        from common import facebook

        facebook.start_crawling(advertiser)
    elif type_id == 2:
        from common import instagram

        instagram.start_crawling(advertiser)
    elif type_id == 3:
        from common import youtube

        youtube.start_crawling(advertiser)
    elif type_id == 4:
        from common import naver_blog

        naver_blog.start_crawling(advertiser)
    elif type_id == 5:
        from common import instagram
        from common import youtube
        from common import naver_blog

        instagram.start_crawling(advertiser)
        youtube.start_crawling(advertiser)
        naver_blog.start_crawling(advertiser)
