import os

from db.raw_db import db_connect, create_table, add_vacancies
from scraper.iaea import IaeaJobScraper
from scraper.irena import IrenaJobScraper
from scraper.iter import IterJobScraper
from scraper.oecd import OecdJobScraper
from web.config import configure_driver

# Path to chrome browser driver.
chromedriver_path = os.path.join(os.getcwd(), 'web', 'chromedriver')

# IAEA job page url.
IAEA_URL = 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl'
# IRENA job page url.
IRENA_URL = 'https://employment.irena.org/careersection/1/joblist.ftl'
# OECD job page url.
OECD_URL = 'https://oecd.taleo.net/careersection/ext/joblist.ftl'
# ITER job page url.
ITER_URL = 'https://www.iter.org/jobs'


# Create driver object.
driver = configure_driver()
# Create scraper object.
scraper = IterJobScraper(driver=driver, link=ITER_URL, timeout=3)
# Scrape jobs - brief info.
scraper.scrape_brief()

# TODO: check if vacancies in scraper.jobs already exist in db.

# Scrape jobs - full info.
scraper.scrape_full()

# Connect to db.
conn = db_connect('jobs.sqlite')
# Create table.
create_table(conn)
# Insert jobs info into table.
add_vacancies(scraper.jobs, conn)
