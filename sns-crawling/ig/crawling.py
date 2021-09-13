import json
from datetime import datetime

import requests


def instgram_login():
    LOGIN_INFO = {
        'username': 'kij@pidaworks.com',
        'password': 'gmsgms0408!',
        'queryParams': "{}"
    }
    link = 'https://www.instagram.com/accounts/login/'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    time = int(datetime.now().timestamp())
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    response = requests.get(link, headers=headers)
    for key in response.cookies:
        print(key)
    csrf = response.cookies['csrftoken']

    payload = {
        'username': LOGIN_INFO['username'],
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{LOGIN_INFO["password"]}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    login_header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    }

    login_response = requests.post(login_url, data=payload, headers=login_header)
    json_data = json.loads(login_response.text)

    if json_data["authenticated"]:

        print("login successful")
        cookies = login_response.cookies
        cookie_jar = cookies.get_dict()
        csrf_token = cookie_jar['csrftoken']
        print("csrf_token: ", csrf_token)
        session_id = cookie_jar['sessionid']
        print("session_id: ", session_id)

        cookies = {
            "sessionid": session_id,
            "csrftoken": csrf_token
        }

        return cookies
    else:
        print("login failed ", login_response.text)
        return None
