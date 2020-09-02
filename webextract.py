"""
This module contains classes used for extracting parameters of teams from webpage sources
"""

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

filename = "data/betfair.com.1.html"

# Attempt1: try to simulate mouse hover actions on the button elements to get the data:

with webdriver.Chrome("/usr/lib/chromium-browser/chromedriver") as driver:
    # temporary hack, ideally we should rather wait for an element to become clickable, for instance:
    driver.implicitly_wait(15)
    driver.get("https://www.betfair.com/exchange/plus/en/football/uefa-euro-2020-betting-28814228")

    for e in driver.find_elements_by_class_name("lay mv-bet-button lay-button lay-selection-button"):
        actions = ActionChains(driver)
        actions.move_to_element(e)
        actions.perform()

    content = driver.page_source
    with open(filename, "w") as f:
        f.write(content)


# Try to get the data from

with open(filename) as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

teams = [t.get_text() for t in soup.find_all("h3", {"class": "runner-name"})]
print(teams)

# Buttons with this class should contain the O/P in title attributes:
buttons = soup.find_all("button", {"class": "lay mv-bet-button lay-button lay-selection-button"})

# Tets: see if there are any title attributes in any buttons, at all:
l = [b.get('title') for b in soup.find_all("button") if b.get('title')]
print(l)





