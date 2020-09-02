"""
This script extracts odds/probability information per team from specific webpages
"""

from lxml import html
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import logging

log = logging.getLogger('root')

# TODO: create a setup script that ensures the selenium driver is installed and is on the PATH

class DynamicContentBase:
    """Base class for common operations with Selenium to populate the document
       with dynamically generated data by simulating user interaction"""
    def __init__(self, driver, base_url, max_timeout=30):
        self.driver = driver
        self.base_url = base_url
        self.max_timeout = max_timeout
        self.wdwait = WebDriverWait(self.driver, self.max_timeout)

    def get_clickable_element(self, xpath):
        "Waits for the element to become clickable before returning it"
        return self.wdwait.until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))

    def click(self, xpath, hint=None):
        "Performs click action on an element specified by XPATH expression and returns the element"
        if hint:
            log.debug(hint)
        e = self.get_clickable_element(xpath)
        ActionChains(self.driver).move_to_element(e).click(e).perform()
        return e

    def send_keys(self, xpath, input_text, hint=None):
        "Types text into input element specified by XPATH"
        if hint:
            log.debug(hint)
        else:
            log.debug("Typing %s" % input_text)
        e = self.get_clickable_element(xpath)
        e.send_keys(input_text)
        return e

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
    def __init__(self, content):
        self.teams = []
        self.odds = []
        self.content = content
        self.extract()

    def extract(self):
        "This method extracts the team names and the O/P values"
        raise NotImplemented

#####################

class PaddyPowerDynamicData(DynamicContentBase):
    def __init__(self, driver, max_timeout=30):
        super().__init__(driver=driver, base_url="https://www.paddypower.com", max_timeout=max_timeout)

    def prepare_page_content(self):
        self.click("//a[2]/span", hint='Clicking "search"')
        self.click("//abc-search-bar/div/input", hint='Clicking search input box')
        self.send_keys("//abc-search-bar/div/input", "uefa euro 2020")
        self.click("//abc-search-result-item/div/div/div", hint='Clicking on first search result')
        self.click("//div[2]/abc-card/div/div/abc-card-content/abc-accordion/div/div/div[2]/div",
                   hint='Expanding the "EURO 2020 Winner" section')
        # ox.click("//abc-link/a/span", hint='Clicking on "Show More"')
        # Clicking on the "Show More" link will not work with Selenium actions, using Javascript instead:
        js = """var x = document.querySelectorAll(".outright-item-show-all > a:nth-child(1)");
                angular.element(x).triggerHandler('click')"""
        self.driver.execute_script(js)

class PaddyPowerOdds(OddsBaseData):
    def __init__(self, content):
        super().__init__(content)

    def extract(self):
        tree = html.fromstring(self.content)
        # Explanation to the XPATH:
        # Find elements only under the second 'outright-coupon-card-items' element:
        # Team names are like: <p class="outright-item__runner-name">Spain</p>
        # Odds are like: <span class="btn-odds__label">15/2</span>
        # class="outright-item__runner-name"
        self.teams = [e.text for e in tree.xpath('//outright-coupon-card-items/div[2]//p[@class="outright-item__runner-name"]') ]
        self.odds = [e.text for e in tree.xpath('//outright-coupon-card-items/div[2]//span[@class="btn-odds__label"]')]

class BetFairDynamicData(DynamicContentBase):
    def __init__(self, driver, max_timeout=30):
        super().__init__(driver=driver, base_url="https://www.betfair.com", max_timeout=max_timeout)

    def prepare_page_content(self):
        pass
        #self.click("//a[2]/span", hint='Clicking "search"')
        #self.send_keys("//abc-search-bar/div/input", "uefa euro 2020")

class BetFairExtractor(OddsBaseData):
    def __init__(self, content):
        super().__init__(content)

    def extract(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        #self.teams = [e.get_text() for e in soup.find_all("p", {"class": "outright-item__runner-name"})]
        #self.opps = [e.get_text() for e in soup.find_all("span", {"class": "btn-odds__label"})]

if __name__ == '__main__':
    with webdriver.Chrome() as driver:
        paddy_dynamic_data = PaddyPowerDynamicData(driver)
        paddy =  PaddyPowerOdds(paddy_dynamic_data.get_content())
        print(paddy.teams)
        print(paddy.odds)

    #with open("data/paddypower.com.html", "w") as f:
    #    f.write(driver.page_source)


# Buttons with this class should contain the O/P in title attributes:
#buttons = soup.find_all("button", {"class": "lay mv-bet-button lay-button lay-selection-button"})

# Tets: see if there are any title attributes in any buttons, at all:
#l = [b.get('title') for b in soup.find_all("button") if b.get('title')]
#print(l)





