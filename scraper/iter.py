import random
import re

from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from dateutil import parser


class IterJobScraper(object):
	"""
	ITER job scraper.
	"""

	def __init__(self, driver, link: str, timeout: float):
		"""
		:param driver: preconfigured webdriver (result of "configure_driver" function)
		:param link: ITER job page url to scrape
		:param timeout: webdriver wait time for page loading
		"""
		# browser driver
		self.driver = driver
		# display resolution
		self.driver.set_window_size(2560, 1600)
		# timeout
		self.wait = WebDriverWait(self.driver, timeout)
		# jobs page link
		self.link = link
		# list of jobs info dictionaries
		self.jobs = None

	def scrape_brief(self):
		"""
		Get general info for currently open vacancies.
		"""
		# get page
		self.driver.get(self.link)
		# create empty jobs list
		jobs = []
		# get page source
		s = BeautifulSoup(self.driver.page_source, features="html.parser")
		# regex to get the job unique id from the job's link
		reg = re.compile(r'id=(\d+)')
		# find all 'tr' tags within the jobs table
		for tr in tqdm(s.tbody.findAll('tr'), desc="Scraping ITER's jobs"):
			# find 'b' tag
			b = tr.findChildren('b')
			# get 'a' tag inside 'b' tag (for job title and link)
			a = b[0].findChildren('a')
			# find all 'td' tags inside 'tr' (job deadline)
			td = tr.findAll('td')
			# create dictionary for each job
			job = {}
			# parse job title
			job_title = a[0].text
			# parse job link from 'href' and join with the site link
			job_link = a[0]['href']
			# add info to job's dictionary
			job['id'] = job_title.split()[-1] + '/' + re.findall(reg, job_link)[0]
			job['title'] = job_title
			job['url'] = job_link
			# parse deadline form the first 'td' tag for current job
			job['deadline'] = parser.parse(td[0].text)
			# specify location manually
			job['location'] = 'France-St. Paul-lez-Durance)'
			# add organization name manually
			job['organization'] = 'ITER'
			# append job's dictionary to overall jobs list
			jobs.append(job)
			# sleep random time after each job
			sleep(random.uniform(0.5, 1.0))

		# save jobs list to class attribute
		self.jobs = jobs

	def scrape_full(self):
		"""
		Update jobs attribute with full info for currently open vacancies.
		The full info is not parsed and and placed into jobs dictionary as html code.
		"""
		reopen_status = re.compile(r'This is a re-opening of the vacancy')  # might be redundant for ITER
		# for each job in jobs list
		for job in tqdm(self.jobs, desc="Getting ITER's jobs descriptions"):
			# go to job description page
			self.driver.get(job['url'])
			# get page source
			s = BeautifulSoup(self.driver.page_source, features="html.parser")

			if re.search(reopen_status, s.text):
				# true if found re-opening status
				job['reopen'] = 1
			else:
				# false otherwise
				job['reopen'] = 0

			# save html code of a job's page
			job['html_page'] = s.prettify(formatter="html")
			# sleep random time after each job
			sleep(random.uniform(0.75, 1.0))

		# close driver after getting all the jobs info
		self.driver.quit()
