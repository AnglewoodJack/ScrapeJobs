from scraper.iaea import IaeaJobScraper
from web.config import configure_driver


# Create driver object.
driver = configure_driver('/Users/ivanandrusin/Desktop/chromedriver')
# Create scraper object.
scraper_iaea = IaeaJobScraper(driver, 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl')
# Scrape jobs
jobs_iaea = scraper_iaea.scrape_brief()
