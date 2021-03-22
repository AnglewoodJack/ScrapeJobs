import random
import re

from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from dateutil import parser


class OecdJobScraper(object):
    """
    OECD job scraper.
    """

    def __init__(self, driver, link: str, timeout: float):
        """
        :param driver: preconfigured webdriver (result of "configure_driver" function)
        :param link: OECD job page url to scrape
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
        # regex for number of jobs (example: Jobs - Page 1 out of 2)
        reg_pages = re.compile(r'\d+ out of (\d+)')
        # apply regex for number of jobs search to page (tag: currentPageInfo): d - reference to driver object
        f = lambda d: re.findall(reg_pages, d.find_element_by_class_name('pagerlabel').text)
        # wait until f is done
        self.wait.until(f)
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
            for i in tqdm(range(1, jobs_number + 1), desc=f'Scraping page {pageno}'):
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
        # for each job in jobs list
        for job in tqdm(self.jobs, desc='Getting job descriptions'):
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
            # save html code of a job's page
            job['html_page'] = s.prettify(formatter='html')
            # sleep random time after each job
            sleep(random.uniform(0.75, 1.0))
        # close driver after getting all the jobs info
        self.driver.quit()
