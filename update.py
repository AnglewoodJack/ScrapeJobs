from db.raw_db import add_vacancies
from scraper.iaea import IaeaJobScraper
from scraper.irena import IrenaJobScraper
from scraper.iter import IterJobScraper
from scraper.oecd import OecdJobScraper
from web.config import configure_driver


# IAEA job page url.
IAEA_URL = 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl'
# IRENA job page url.
IRENA_URL = 'https://employment.irena.org/careersection/1/joblist.ftl'
# OECD job page url.
OECD_URL = 'https://oecd.taleo.net/careersection/ext/joblist.ftl'
# ITER job page url.
ITER_URL = 'https://www.iter.org/jobs'


def update_db(conn):
    """"""
    # Create driver object.
    driver = configure_driver()
    iaea = IaeaJobScraper(driver=driver, link=IAEA_URL, timeout=3)
    # Scrape jobs - brief info.
    iaea.scrape_brief()
    # Scrape jobs - full info.
    iaea.scrape_full()
    # Insert jobs info into table.
    add_vacancies(iaea.jobs, conn)

    driver = configure_driver()
    irena =  IrenaJobScraper(driver=driver, link=IRENA_URL, timeout=3)
    # Scrape jobs - brief info.
    irena.scrape_brief()
    # Scrape jobs - full info.
    irena.scrape_full()
    # Insert jobs info into table.
    add_vacancies(irena.jobs, conn)

    driver = configure_driver()
    oecd = OecdJobScraper(driver=driver, link=OECD_URL, timeout=3)
    # Scrape jobs - brief info.
    oecd.scrape_brief()
    # Scrape jobs - full info.
    oecd.scrape_full()
    # Insert jobs info into table.
    add_vacancies(oecd.jobs, conn)

    driver = configure_driver()
    iter = IterJobScraper(driver=driver, link=ITER_URL, timeout=3)
    # Scrape jobs - brief info.
    iter.scrape_brief()
    # iter jobs - full info.
    iter.scrape_full()
    # Insert jobs info into table.
    add_vacancies(iter.jobs, conn)
