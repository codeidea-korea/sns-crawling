from selenium import webdriver

from conf import config
from . import util


def get_driver(headless=False):
    os = util.get_os()

    driver_name = ""
    if os == "linux":
        driver_name = "chromedriver-linux"
    elif os == "windows":
        driver_name = "chromedriver.exe"
    elif os == "mac":
        driver_name = "chromedriver-mac"

    driver_path = config.driver_path + "/drivers/" + driver_name

    # chrome driver options
    options = webdriver.ChromeOptions()
    if headless is True:
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

        # options.add_argument("--no-sandbox")
        # options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Chrome(driver_path, chrome_options=options)

    return driver
