from db.raw_db import add_vacancies
from core.scraper import IaeaScraper, IrenaScraper, IterScraper, OecdScraper
from config.config import configure_driver

# Path to chrome browser driver.
CHROME_PATH = "/usr/local/bin/chromedriver"  # MacOs default folder after chromedriver installation with brew
# IAEA job page url.
IAEA_URL = 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl'
# IRENA job page url.
IRENA_URL = 'https://employment.irena.org/careersection/1/joblist.ftl'
# OECD job page url.
OECD_URL = 'https://oecd.taleo.net/careersection/ext/joblist.ftl'
# ITER job page url.
ITER_URL = 'https://www.iter.org/jobs'

# Create all scrapers.
scrapers = [
    IaeaScraper(driver=None, link=IAEA_URL, timeout=3),
    IrenaScraper(driver=None, link=IRENA_URL, timeout=3),
    OecdScraper(driver=None, link=OECD_URL, timeout=3),
    IterScraper(driver=None, link=ITER_URL, timeout=3)
]


def update_db(conn):
    """
    Scrape jobs from IAEA, IRENA, OECD and ITER websites.
    :param conn: db connection object.
    """
    for scraper in scrapers:
        # Create driver object.
        driver = configure_driver()  # specify chromedriver path if needed
        # Assign driver to core instance.
        scraper.driver = driver
        # Scrape jobs - brief info.
        scraper.scrape_brief()
        # Scrape jobs - full info.
        scraper.scrape_full()
        # Insert jobs info into table.
        add_vacancies(scraper.jobs, conn)
