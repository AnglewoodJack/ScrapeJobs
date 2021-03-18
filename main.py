from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


import re
from tqdm import tqdm
import random
from urllib.parse import urljoin
from time import sleep












def scrape(self, get_html=True, quit_driver=True):
	"""

	"""
	# scrape brief info
	self.scrape_brief()
	# scrape full info
	if get_html:
		self.scrape_job_descriptions(jobs)

	# close driver session
	if quit_driver:
		self.driver.quit()

	return jobs





# create the driver object.
driver = configure_driver('/Users/ivanandrusin/Desktop/chromedriver')

scraper_iaea = IaeaJobScraper(driver, 'https://iaea.taleo.net/careersection/ex/jobsearch.ftl')
jobs_iaea = scraper_iaea.scrape(get_html=True, quit_driver=True)