import random
import re
from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


class IterJobScraper(object):
	"""

	"""

	def __init__(self, driver, link):
		# browser driver
		self.driver = driver
		# display resolution
		self.driver.set_window_size(2560, 1600)
		# timeout
		self.wait = WebDriverWait(self.driver, 10)
		# jobs page link
		self.link = link

	def scrape_job_links(self):
		"""

		"""
		# get page
		self.driver.get(self.link)
		# create empty jobs list
		jobs = []
		# get page soucce
		s = BeautifulSoup(self.driver.page_source)
		# regex to get the job unique id from the job's link
		reg = re.compile(r'id=(\d+)')
		# find all 'tr' tags within the jobs table
		for tr in tqdm(s.tbody.findAll('tr'), desc='Scraping jobs'):
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
			job['deadline'] = td[0].text
			# append job's dictionary to overall jobs list
			jobs.append(job)
			# sleep random time after each job
			sleep(random.uniform(0.5, 1.0))

		return jobs

	def scrape_job_descriptions(self, jobs):
		"""

		"""
		# for each job in jobs list
		for job in tqdm(jobs, desc='Getting job descriptions'):
			# go to job description page
			self.driver.get(job['url'])
			# get page source
			s = BeautifulSoup(self.driver.page_source)
			# save html code of a job's page
			job['html_page'] = s.prettify(formatter="html")
			# sleep random time after each job
			sleep(random.uniform(0.75, 1.0))

	def scrape(self, get_html=True, quit_driver=True):
		"""

		"""
		# scrape brief info
		jobs = self.scrape_job_links()
		# scrape full info
		if get_html:
			self.scrape_job_descriptions(jobs)

		# close driver session
		if quit_driver:
			self.driver.quit()

		return jobs
