class IaeaJobScraper(object):
	"""
	IAEA jobs scraper.
	"""

	def __init__(self, driver: object, link: str, timeout: float):
		"""
		:param driver: preconfigured webdriver (result of "configure_driver" function)
		:param link: linc to scraping webpage - iaea.taleo.net
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
		# go to jobs page
		self.driver.get(self.link)
		# regex for number of jobs (example: Job Openings 1 - 25 of 33)
		reg_pages = re.compile(r'\d+ - \d+ of \d+')
		# apply regex to search for a number of jobs at page (tag: currentPageInfo): d - reference to driver object
		f = lambda d: re.search(reg_pages, d.find_element_by_id('currentPageInfo').text)
		# wait until f is done
		self.wait.until(f)
		# execute f
		match_res = f(self.driver)
		# match_object.group(0) says that the whole part of match_object is chosen.
		page_res = match_res.group(0) # get string
		# create empty jobs list
		jobs = []
		# initialize page number
		pageno = 1
		# loop through pages and jobs
		while True:
			# get page source code
			s = BeautifulSoup(self.driver.page_source)
			# regex to find job's link
			job_reg = re.compile(r'jobdetail\.ftl\?job=\d+')
			# regex to find job's id
			id_reg = re.compile(r'job=(\d+\/\d+\s\(\d+\))')
			# find all 'a' tags with 'href' of specified above regex pattern
			for a in tqdm(s.findAll('a', href=job_reg), desc=f'Scraping page {pageno}'):
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
				# append job's dictionary to overall jobs list
				jobs.append(job)
				# sleep random time after each job
				sleep(random.uniform(0.5,1.0))

			# find next page button
			next_page_elem = self.driver.find_element_by_id('next')
			# check if next page exists
			next_page_link = s.find('a', text=f'{pageno + 1}')
			# if next page exists
			if next_page_link:
				# go to the next page
				next_page_elem.click()
				# check if page has changed - example: transition from  "1 - 25 of 48" to "26 - 50 of 48"
				self.wait.until(lambda d: f(d) and f(d).group(0) != page_res)
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
		Update jobs attribute wuth full info for currently open vacancies.
		The full info is not parsed and and placed into jobs dictionary as html code.
		"""
		# for each job in jobs list
		for job in tqdm(self.jobs, desc='Getting job descriptions'):
			# go to job description page
			self.driver.get(job['url'])
			# get page source
			s = BeautifulSoup(self.driver.page_source)
			# save html code of a job's page
			job['html_page'] = s.prettify(formatter='html')
			# sleep random time after each job
			sleep(random.uniform(0.75,1.0))
		# close driver after getting all the jobs info
		self.driver.quit()
