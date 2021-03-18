class OecdJobScraper(object):

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
		# regex for number of jobs (example: Jobs - Page 1 out of 2)
		reg_pages = re.compile(r'\d+ out of (\d+)')
		# apply regex for number of jobs search to page (tag: currentPageInfo): d - reference to driver object
		f = lambda d: re.findall(reg_pages, d.find_element_by_id('requisitionListInterface.pagerDivID1649.Label').text)
		# wait until f is done
		self.wait.until(f)
		# execute f
		m = f(self.driver)
		# get total number of pages
		total_pages = int(m[0])
		# get the number of jobs per page
		select = Select(driver.find_element_by_name('dropListSize'))
		per_page = int(select.first_selected_option.text)
		# get total number of jobs
		total_jobs = int(re.findall(r'\d+', driver.find_element_by_id('requisitionListInterface.ID745').text)[0])
		# create empty jobs list
		jobs = []
		# set initial page number
		pageno = 1

		while pageno <= total_pages:
			# count jobs at page
			job_count = 1
			# go to corresponding page
			driver.find_element_by_id(f'requisitionListInterface.pagerDivID1649.P{pageno}').click()
			# wait for the page to be loaded
			sleep(3)
			# check the number of jobs on a page
			if total_jobs > per_page:
				jobs_number = per_page
				total_jobs -= per_page
			else:
				jobs_number = total_jobs

			# loop through jobs on the page
			for i in tqdm(range(1, jobs_number + 1), desc=f'Scraping page {pageno}'):
				# job's info dictionary initialization
				job = {}
				# add job title
				_title = driver.find_element_by_id(f'requisitionListInterface.reqTitleLinkAction.row{i}')
				job['title'] = _title.text
				# add OECD organization
				_oecd_unit = driver.find_element_by_id(f'requisitionListInterface.reqOrganization.row{i}')
				job['oecd_unit'] = _oecd_unit.text
				# add job location
				_location = driver.find_element_by_id(f'requisitionListInterface.reqBasicLocation.row{i}')
				job['location'] = _location.text
				# add job posting date
				_posted = driver.find_element_by_id(f'requisitionListInterface.reqPostingDate.row{i}')
				job['posted'] = _posted.text
				# add job id
				_id = driver.find_element_by_id(f'requisitionListInterface.reqContestNumberValue.row{i}')
				job['id'] = _id.text
				# add job deadline
				_deadline = driver.find_element_by_id(f'requisitionListInterface.reqUnpostingDate.row{i}')
				job['deadline'] = _deadline.text
				# add job position on the page
				job['page/row'] = (pageno, i)
				# update job counter
				job_count += 1
				# append job's dictionary to overall jobs list
				jobs.append(job)
				# sleep random time after each job
				sleep(random.uniform(0.5,1.0))
			# update page number
			pageno += 1

		return jobs

	def scrape_job_descriptions(self, jobs):
		"""

		"""
		# for each job in jobs list
		for job in tqdm(jobs, desc='Getting job descriptions'):
			# go to job description page
			self.driver.get(self.link)
			# find jobs page
			page_elem = self.driver.find_element_by_id(f'requisitionListInterface.pagerDivID1649.P{job["page/row"][0]}')
			# go to page
			page_elem.click()
			# find job
			row = self.driver.find_element_by_id(f'requisitionListInterface.reqTitleLinkAction.row{job["page/row"][1]}')
			# go to current job page
			row.click()
			# get page source
			s = BeautifulSoup(self.driver.page_source)
			# save html code of a job's page
			job['html_page'] = s.prettify(formatter='html')
			# sleep random time after each job
			sleep(random.uniform(0.75,1.0))

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
