import os

from scraper.iaea import IaeaJobScraper
from web.config import configure_driver

# Path to chrome browser driver.
chromedriver_path = os.path.join(os.getcwd(), 'web', 'chromedriver')
# IAEA job page url.
iaea_url = 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl'
# Create driver object.
driver = configure_driver()
# Create scraper object.
scraper_iaea = IaeaJobScraper(driver=driver, link=iaea_url, timeout=3)
# Scrape jobs
scraper_iaea.scrape_brief()

for i in scraper_iaea.jobs:
	print(i)
