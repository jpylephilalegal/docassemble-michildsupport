from aloe import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import ChromeOptions, Chrome
import time
import os
from webdriver_manager.chrome import ChromeDriverManager

default_path = "https://micase.state.mi.us/calculatorapp/public/welcome/load.html"
default_wait_seconds = 0
use_headless_chrome = True

class MyChrome(Chrome):
    def loaded(self):
        try:
            return 0 == self.execute_script("return jQuery.active")
        except WebDriverException:
            pass

    def wait_for_it(self):
        WebDriverWait(self, 20).until(MyChrome.loaded, "Timeout waiting for page to load")

    def text_present(self, text):
        try:
            body = self.find_element_by_tag_name("body")
        except NoSuchElementException:
            return False
        return text in body.text

@before.all
def setup_browser():
    world.screenshot_number = 0
    world.screenshot_folder = None
    world.headless = False
    if use_headless_chrome:
        world.headless = True
        options = ChromeOptions()
        options.add_argument("--window-size=1350,7000")
        options.add_argument("--headless");
        options.add_argument("--no-sandbox");
        world.browser = MyChrome(ChromeDriverManager().install(), chrome_options=options)
    else:
        options = ChromeOptions()
        options.add_argument("--start-maximized");
        world.browser = MyChrome(ChromeDriverManager().install(), chrome_options=options)
    world.default_path = default_path
    world.wait_seconds = default_wait_seconds

@after.all
def tear_down():
    time.sleep(2)
    world.browser.quit()
