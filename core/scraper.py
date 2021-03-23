import random
import re

from time import sleep
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from dateutil import parser


class JobScraper:
	"""
	Job core.
	"""

	def __init__(self, driver, link: str, timeout: float):
		"""
		:param driver: preconfigured webdriver (result of "configure_driver" function)
		:param link: IAEA job page url to scrape
		:param timeout: webdriver wait time for page loading
		"""
		# browser driver
		self.driver = driver
		# timeout
		self.timeout = timeout
		# jobs page link
		self.link = link
		# list of jobs info dictionaries
		self.jobs = None

	def scrape_brief(self):
		"""
		Scrape function template.
		"""
		pass

	def scrape_full(self):
		"""
		Scrape function template.
		"""
		pass


class IaeaScraper(JobScraper):
	"""
	IAEA job core.
	"""

	def scrape_brief(self):
		"""
		Get general info for currently open vacancies.
		"""
		# go to jobs page
		self.driver.get(self.link)
		# regex for number of jobs (example: Job Openings 1 - 25 of 33)
		reg_pages = re.compile(r'\d+ - \d+ of \d+')
		# apply regex to search for a number of jobs at page (tag: currentPageInfo): d - reference to driver object
		f = lambda d: re.search(reg_pages, d.find_element_by_id('currentPageInfo').text)
		# wait until f is done
		WebDriverWait(self.driver, self.timeout).until(f)
		# execute f
		match_res = f(self.driver)
		# match_object.group(0) says that the whole part of match_object is chosen.
		page_res = match_res.group(0)  # get string
		# create empty jobs list
		jobs = []
		# initialize page number
		pageno = 1
		# loop through pages and jobs
		while True:
			# get page source code
			s = BeautifulSoup(self.driver.page_source, features="html.parser")
			# regex to find job's link
			job_reg = re.compile(r'jobdetail\.ftl\?job=\d+')
			# regex to find job's id
			id_reg = re.compile(r'job=(\d+\/\d+\s\(\d+\))')
			# find all 'a' tags with 'href' of specified above regex pattern
			for a in tqdm(s.findAll('a', href=job_reg), desc=f"Scraping IAEA's job page {pageno}"):
				# for each 'a' tag find parent 'tr' and 'td' tags
				tr = a.findParent('tr')
				td = tr.findAll('td')
				# create dictionary for each job
				job = {}
				# parse job link from 'href' and join with the site link
				job_link = urljoin(self.link, a['href'])
				# add info to job's dictionary
				# add job id
				job['id'] = re.findall(id_reg, job_link)[0]
				# add job title
				job['title'] = a.text
				# add job link
				job['url'] = job_link
				# parse location form the second 'td' tag for current job
				job['location'] = td[1].text
				# parse deadline form the third 'td' tag for current job
				job['deadline'] = parser.parse(td[2].text)
				# add organization name manually
				job['organization'] = 'IAEA'
				# append job's dictionary to overall jobs list
				jobs.append(job)
				# sleep random time after each job
				sleep(random.uniform(0.5, 1.0))

			# find next page button
			next_page_elem = self.driver.find_element_by_id('next')
			# check if next page exists
			next_page_link = s.find('a', text=f'{pageno + 1}')
			# if next page exists
			if next_page_link:
				# go to the next page
				next_page_elem.click()
				# check if page has changed - example: transition from  "1 - 25 of 48" to "26 - 50 of 48"
				WebDriverWait(self.driver, self.timeout).until(lambda d: f(d) and f(d).group(0) != page_res)
				# repeat search for number og jobs per page operations
				match_res = f(self.driver)
				page_res = match_res.group(0)
				# update page number
				pageno += 1
			else:
				# stop loop if no pages left
				break

		# save jobs list to class attribute
		self.jobs = jobs

	def scrape_full(self):
		"""
		Update jobs attribute with full info for currently open vacancies.
		The full info is not parsed and and placed into jobs dictionary as html code.
		"""
		# check if it is a re-opening of the vacancy
		reopen_status = re.compile(r'This is a re-opening of the vacancy')
		# for each job in jobs list
		for job in tqdm(self.jobs, desc="Getting IAEA's job descriptions"):
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
			job['html_page'] = s.prettify(formatter='html')
			# sleep random time after each job
			sleep(random.uniform(0.75, 1.0))
		# close driver after getting all the jobs info
		self.driver.quit()


class IrenaScraper(JobScraper):
	"""
	IRENA job core.
	"""

	def scrape_brief(self):
		"""
		Get general info for currently open vacancies.
		"""
		# get page
		self.driver.get(self.link)
		# regex for number of jobs (example: Jobs - Page 1 out of 2)
		reg_pages = re.compile(r'\d+ out of (\d+)')
		# apply regex for number of jobs search to page (tag: currentPageInfo): d - reference to driver object
		f = lambda d: re.findall(reg_pages, d.find_element_by_id('content').text)
		# wait until f is done
		WebDriverWait(self.driver, self.timeout).until(f)
		# execute f
		m = f(self.driver)
		# get total number of pages
		total_pages = int(m[0])
		# get the number of jobs per page
		select = Select(self.driver.find_element_by_name('dropListSize'))
		per_page = int(select.first_selected_option.text)
		# get total number of jobs
		total_jobs = int(re.findall(r'\d+', self.driver.find_element_by_class_name('subtitle').text)[0])
		# create empty jobs list
		jobs = []
		# set initial page number
		pageno = 1

		while pageno <= total_pages:
			# go to corresponding page
			self.driver.find_element_by_xpath(f'//*[@title="Go to page {pageno}"]').click()
			# wait for the page to be loaded
			sleep(3)
			# check the number of jobs on a page
			if total_jobs > per_page:
				jobs_number = per_page
				total_jobs -= per_page
			else:
				jobs_number = total_jobs

			# loop through jobs on the page
			for i in tqdm(range(1, jobs_number + 1), desc=f"Scraping IRENA's job page {pageno}"):
				# job's info dictionary initialization
				job = {}
				# add job title
				_title = self.driver.find_element_by_id(f'requisitionListInterface.reqTitleLinkAction.row{i}')
				job['title'] = _title.text
				# add job location
				_location = self.driver.find_element_by_id(f'requisitionListInterface.reqBasicLocation.row{i}')
				job['location'] = _location.text
				# add job posting date
				_posted = self.driver.find_element_by_id(f'requisitionListInterface.reqPostingDate.row{i}')
				job['posted'] = _posted.text
				# add job id
				_id = self.driver.find_element_by_id(f'requisitionListInterface.reqContestNumberValue.row{i}')
				job['id'] = _id.text
				# add job deadline
				_deadline = self.driver.find_element_by_id(f'requisitionListInterface.reqUnpostingDate.row{i}')
				job['deadline'] = parser.parse(_deadline.text)
				# add organization name manually
				job['organization'] = 'IRENA'
				# add job position on the page
				job['page/row'] = (pageno, i)
				# append job's dictionary to overall jobs list
				jobs.append(job)
				# sleep random time after each job
				sleep(random.uniform(0.5, 1.0))
			# update page number
			pageno += 1

		self.jobs = jobs

	def scrape_full(self):
		"""
		Update jobs attribute with full info for currently open vacancies.
		The full info is not parsed and and placed into jobs dictionary as html code.
		"""
		# check if it is a re-opening of the vacancy
		reopen_status = re.compile(r'This is a re-opening of the vacancy')  # might be redundant for IRENA
		# for each job in jobs list
		for job in tqdm(self.jobs, desc="Getting IRENA's job descriptions"):
			# go to job description page
			self.driver.get(self.link)
			# find jobs page
			page_elem = self.driver.find_element_by_xpath(f'//*[@title="Go to page {job["page/row"][0]}"]')
			# go to page
			page_elem.click()
			# wait for the page to load
			sleep(random.uniform(0.75, 1.0))
			# find job
			row = self.driver.find_element_by_id(f'requisitionListInterface.reqTitleLinkAction.row{job["page/row"][1]}')
			# go to current job page
			row.click()
			# get page source
			s = BeautifulSoup(self.driver.page_source, features="html.parser")

			if re.search(reopen_status, s.text):
				# true if found re-opening status
				job['reopen'] = 1
			else:
				# false otherwise
				job['reopen'] = 0

			# save html code of a job's page
			job['html_page'] = s.prettify(formatter='html')
			# sleep random time after each job
			sleep(random.uniform(0.75, 1.0))
		# close driver after getting all the jobs info
		self.driver.quit()


class IterScraper(JobScraper):
	"""
	ITER job core.
	"""

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
		for tr in tqdm(s.tbody.findAll('tr'), desc="Scraping ITER jobs"):
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
		for job in tqdm(self.jobs, desc="Getting ITER's job descriptions"):
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


class OecdScraper(JobScraper):
	"""
	OECD job core.
	"""

	def scrape_brief(self):
		"""
		Get general info for currently open vacancies.
		"""
		# get page
		self.driver.get(self.link)
		# regex for number of jobs (example: Jobs - Page 1 out of 2)
		reg_pages = re.compile(r'\d+ out of (\d+)')
		# apply regex for number of jobs search to page (tag: currentPageInfo): d - reference to driver object
		f = lambda d: re.findall(reg_pages, d.find_element_by_class_name('pagerlabel').text)
		# wait until f is done
		WebDriverWait(self.driver, self.timeout).until(f)
		# execute f
		m = f(self.driver)
		# get total number of pages
		total_pages = int(m[0])
		# get the number of jobs per page
		select = Select(self.driver.find_element_by_name('dropListSize'))
		per_page = int(select.first_selected_option.text)
		# get total number of jobs
		total_jobs = int(re.findall(r'\d+', self.driver.find_element_by_class_name('subtitle').text)[0])
		# create empty jobs list
		jobs = []
		# set initial page number
		pageno = 1

		while pageno <= total_pages:
			# go to corresponding page
			self.driver.find_element_by_xpath(f'//*[@title="Go to page {pageno}"]').click()
			# wait for the page to be loaded
			sleep(3)
			# check the number of jobs on a page
			if total_jobs > per_page:
				jobs_number = per_page
				total_jobs -= per_page
			else:
				jobs_number = total_jobs

			# loop through jobs on the page
			for i in tqdm(range(1, jobs_number + 1), desc=f"Scraping OECD's job page {pageno}"):
				# job's info dictionary initialization
				job = {}
				# add job title
				_title = self.driver.find_element_by_id(f'requisitionListInterface.reqTitleLinkAction.row{i}')
				job['title'] = _title.text
				# add OECD organization
				_oecd_unit = self.driver.find_element_by_id(f'requisitionListInterface.reqOrganization.row{i}')
				job['oecd_unit'] = _oecd_unit.text
				# add job location
				_location = self.driver.find_element_by_id(f'requisitionListInterface.reqBasicLocation.row{i}')
				job['location'] = _location.text
				# add job posting date
				_posted = self.driver.find_element_by_id(f'requisitionListInterface.reqPostingDate.row{i}')
				job['posted'] = _posted.text
				# add job id
				_id = self.driver.find_element_by_id(f'requisitionListInterface.reqContestNumberValue.row{i}')
				job['id'] = _id.text
				# add job deadline
				_deadline = self.driver.find_element_by_id(f'requisitionListInterface.reqUnpostingDate.row{i}')
				job['deadline'] = parser.parse(_deadline.text)
				# add organization name manually
				job['organization'] = 'OECD'
				# add job position on the page
				job['page/row'] = (pageno, i)
				# append job's dictionary to overall jobs list
				jobs.append(job)
				# sleep random time after each job
				sleep(random.uniform(0.5, 1.0))
			# update page number
			pageno += 1

		self.jobs = jobs

	def scrape_full(self):
		"""
		Update jobs attribute with full info for currently open vacancies.
		The full info is not parsed and and placed into jobs dictionary as html code.
		"""
		# check if it is a re-opening of the vacancy
		reopen_status = re.compile(r'This is a re-opening of the vacancy')  # might be redundant for OECD
		# for each job in jobs list
		for job in tqdm(self.jobs, desc="Getting OECD's job descriptions"):
			# go to job description page
			self.driver.get(self.link)
			# find jobs page
			page_elem = self.driver.find_element_by_xpath(f'//*[@title="Go to page {job["page/row"][0]}"]')
			# go to page
			page_elem.click()
			# wait for the page to load
			sleep(random.uniform(1.0, 1.5))
			# find job
			row = self.driver.find_element_by_id(f'requisitionListInterface.reqTitleLinkAction.row{job["page/row"][1]}')
			# go to current job page
			row.click()
			# get page source
			s = BeautifulSoup(self.driver.page_source, features="html.parser")

			if re.search(reopen_status, s.text):
				# true if found re-opening status
				job['reopen'] = 1
			else:
				# false otherwise
				job['reopen'] = 0

			# save html code of a job's page
			job['html_page'] = s.prettify(formatter='html')
			# sleep random time after each job
			sleep(random.uniform(0.75, 1.0))
		# close driver after getting all the jobs info
		self.driver.quit()
