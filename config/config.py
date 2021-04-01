"""
Selenium driver configuration module.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def configure_driver(path: str = None):
	"""
	Sets chromedriver parameters.
	:params path: path to chromedriver executable.
	:return: configured driver object.
	"""
	# add additional options to webdriver
	chrome_options = Options()
	# add the argument and make the browser Headless.
	chrome_options.add_argument('--headless')
	# ignore errors caused by theck of certificate
	chrome_options.add_argument('--ignore-certificate-errors')
	# use incognito mode
	chrome_options.add_argument('--incognito')
	# instantiate webdriver:
	if path:
		# apply options
		driver = webdriver.Chrome(path, options=chrome_options)
	else:
		# import driver manager
		from webdriver_manager.chrome import ChromeDriverManager
		# download chrome driver corresponding to chrome browser verwion using driver manager and apply with options
		driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

	return driver
