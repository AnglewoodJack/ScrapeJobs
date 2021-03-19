import os

from scraper.irena import IrenaJobScraper
from web.config import configure_driver

# Path to chrome browser driver.
chromedriver_path = os.path.join(os.getcwd(), 'web', 'chromedriver')

# IAEA job page url.
iaea_url = 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl'
# IRENA job page url.
irena_url = 'https://employment.irena.org/careersection/1/joblist.ftl'


# Create driver object.
driver = configure_driver()
# Create scraper object.
scraper = IrenaJobScraper(driver=driver, link=irena_url, timeout=3)
# Scrape jobs - brief info
scraper.scrape_brief()
# Scrape jobs - full info
scraper.scrape_full()
