#!/usr/bin/python3
"""
This script extracts odds/probability information per team from specific webpages
"""

from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging
import time
import pandas as pd
import argparse
import sys
import contextlib
import concurrent.futures
from collections import namedtuple

logging.basicConfig(filename="%s.log" % sys.argv[0], level=logging.DEBUG)
log = logging.getLogger('root')

# TODO: create a setup script or Docker image that ensures the selenium driver is installed and is on the PATH

# ------------------- BASE CLASSES ----------------------

class DynamicContentBase:
    """Base class for common operations with Selenium to populate the document
       with dynamically generated data by simulating user interaction"""
    def __init__(self, driver, base_url, max_timeout=30):
        self.driver = driver
        self.base_url = base_url
        self.max_timeout = max_timeout
        self.wdwait = WebDriverWait(self.driver, self.max_timeout)
        self.cookies_accepted = False

    def get_clickable_element(self, filter):
        "Waits for the element to become clickable before returning it. This is to avoid race conditions."
        return self.wdwait.until(expected_conditions.element_to_be_clickable(filter))

    def click(self, filter, hint=None):
        "Performs click action on an element specified by XPATH expression and returns the element"
        if hint:
            log.debug(hint)
        e = self.get_clickable_element(filter)
        ActionChains(self.driver).move_to_element(e).click(e).perform()
        return e

    def send_keys(self, filter, input_text, hint=None):
        "Types text into input element specified by XPATH"
        if hint:
            log.debug(hint)
        else:
            log.debug("Typing %s" % input_text)
        e = self.get_clickable_element(filter)
        e.send_keys(input_text)
        return e

    def accept_all_cookies(self):
        """Clicks on the 'accept cookies' button/link
           It does that once only, and also handles timeout, assuming that cookies have been already accepted previously."""
        if not self.cookies_accepted:
            try:
                self.click((By.ID, "onetrust-accept-btn-handler"), hint="Accept cookies")
            except TimeoutException:
                log.debug("Timeout for Accept cookies button: most likely already accepted")
            self.cookies_accepted = True

    def get_content(self):
        "Returns the raw data after transformations"
        log.debug("Opening page %s" % self.base_url)
        self.driver.get(self.base_url)
        self.prepare_page_content()
        return self.driver.page_source

    def prepare_page_content(self):
        "This method sets up the page (dynamic content) and is specific to each web page"
        raise NotImplemented

class OddsBaseData:
    ALIASES = {'Rep Of Ireland': 'Republic of Ireland',
               'Bosnia': 'Bosnia-Herzegovina'}
    def __init__(self):
        self.teams = []
        self.odds = []

    def extract(self, content):
        self.transform(content)
        self.teams = list(map(lambda t: self.ALIASES.get(t,t), self.teams))

    def transform(self, content):
        "This method extracts the team names and the O/P values"
        raise NotImplemented

# ------------------- WEBPAGE-SPECIFIC CLASSES ----------------------

class PaddyPowerDynamicData(DynamicContentBase):
    def __init__(self, driver, max_timeout=60):
        super().__init__(driver=driver, base_url="https://www.paddypower.com", max_timeout=max_timeout)

    def prepare_page_content(self):
        # This is a replay of a manual test case recorded with Firefox plugin 'Katalon Recorder' (~ like Selenium Builder)
        self.accept_all_cookies()
        self.click( (By.XPATH, "//a[2]/span"), hint='Clicking "search"')
        self.click( (By.XPATH, "//abc-search-bar/div/input"), hint='Clicking search input box')
        self.send_keys( (By.XPATH, "//abc-search-bar/div/input"), "uefa euro 2020")
        self.click( (By.XPATH, "//abc-search-result-item/div/div/div"), hint='Clicking on first search result')
        self.click( (By.XPATH, "//div[2]/abc-card/div/div/abc-card-content/abc-accordion/div/div/div[2]/div"),
                   hint='Expanding the "EURO 2020 Winner" section')
        # Clicking on the "Show More" link will not work with Selenium actions, using Javascript instead:
        js = """var x = document.querySelectorAll(".outright-item-show-all > a:nth-child(1)");
                angular.element(x).triggerHandler('click')"""
        self.driver.execute_script(js)

class PaddyPowerOdds(OddsBaseData):
    def __init__(self):
        super().__init__()

    def transform(self, content):
        tree = html.fromstring(content)
        # Explanation to the XPATH expression:
        # Find elements only under the second 'outright-coupon-card-items' element:
        # Team names are like: <p class="outright-item__runner-name">Spain</p>
        # Odds are like: <span class="btn-odds__label">15/2</span>
        # class="outright-item__runner-name"
        self.teams = [e.text for e in tree.xpath('//outright-coupon-card-items/div[2]//p[@class="outright-item__runner-name"]') ]
        self.odds = [e.text for e in tree.xpath('//outright-coupon-card-items/div[2]//span[@class="btn-odds__label"]')]

class BetFairDynamicData(DynamicContentBase):
    def __init__(self, driver, max_timeout=60):
        super().__init__(driver=driver, base_url="https://www.betfair.com", max_timeout=max_timeout)

    def prepare_page_content(self):
        self.accept_all_cookies()
        self.click( (By.ID, "EXCHANGE"), hint="Exchange menu" )
        self.click( (By.LINK_TEXT, "Football"), hint="Football link on left side" )
        self.click( (By.LINK_TEXT, "International"), hint="International link on left side" )
        self.click( (By.LINK_TEXT, "UEFA Euro 2020"), hint="'UEFA Euro 2020' link on left side" )
        self.click( (By.LINK_TEXT, "Winner"), hint="Winner link on left side" )

        js = """var buttons = document.querySelectorAll("button");
                for (i=0; i<buttons.length; i++) {buttons[i].dispatchEvent(new Event('mouseover'));}
             """
        self.driver.execute_script(js)
        # Does it take time to process all those mouseover events? Will it make any difference if we sleep 30 sec?
        # Answer: sometimes this works, sometimes it doesn't
        # Note: I would never do this in a production environment, I am out of ideas now how to ensure these button elements' title attributes get populated.
        # With the lack of information on clearly defined APIs/data sources this exercise was just for the benefit of learning something new.
        time.sleep(30)

class BetFairOdds(OddsBaseData):
    def __init__(self):
        super().__init__()

    def transform(self, content):
        tree = html.fromstring(content)
        self.teams = [e.text for e in tree.xpath('//h3[@class="runner-name"]') ]
        self.odds = [e.get('title', '') for e in tree.xpath('//button[@class="lay mv-bet-button lay-button lay-selection-button"]')]

# ------------------ MAIN SCRIPT ----------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This tool retrieves odds/probability of teams from webpages.")
    parser.add_argument('-o', help='output to file')
    parser.add_argument('-t', help='retrieval period [minutes]', default=5, type=int)
    arg = parser.parse_args()
    if arg.o:
        out = open(arg.o, 'w')
    else: out = sys.stdout

    chrome_options = Options()
    # Note: making the browser headless doesn't really make much difference in performance, and with the GUI it's more spectacular :)
    # I also didn't bother trying different (perhaps lower memory-footprint) selenium drivers, as I believe the whole exercise
    # is not something someone would ever want to produce in a scalable size.
    # chrome_options.add_argument('--headless')

    Page = namedtuple('Page', ['name', 'manipulator', 'extractor'])
    pages = []

    with contextlib.ExitStack() as estack:
        pages.append(Page('BetFair', BetFairDynamicData(estack.enter_context(webdriver.Chrome(options=chrome_options))), BetFairOdds()))
        pages.append(Page('Paddy', PaddyPowerDynamicData(estack.enter_context(webdriver.Chrome(options=chrome_options))), PaddyPowerOdds()))
        while True:
            last_time = time.time()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [ (p, executor.submit(p.manipulator.get_content)) for p in pages ]
                for (p, future) in futures:
                    p.extractor.extract(future.result())

            d = dict([ (p.name, pd.Series(p.extractor.odds, index=p.extractor.teams, dtype=str)) for p in pages])
            df = pd.DataFrame(d)
            out.writelines("%s\n" % str(df))
            sleep_time = max(int(last_time+arg.t*60-time.time()), 0)
            log.debug("Sleeping %ds ..." % sleep_time)
            time.sleep(sleep_time)
