from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

import time

from conf import config
from common import crawl
from common import util
from . import parsing


def get_page(driver, url):
    driver.get(url)
    time.sleep(2)

    util.ec("WAIT LAYOUT")
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, config.facebook_dom["layout"]))
    )

    util.ec("SCROLLING")
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    util.ec("POSTS")
    layout = driver.find_element_by_css_selector(config.facebook_dom["layout"])
    posts = layout.find_elements_by_css_selector(config.facebook_dom["post"])
    data = []

    i = 0
    for post in posts:
        data.append(parsing.parsing(post.get_attribute("outerHTML")))

        i += 1
        # if i > 1:
        #     break

    return data
