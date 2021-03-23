import os

from db.raw_db import db_connect, create_table, get_vacancies
from update import update_db


# Path to chrome browser driver.
chromedriver_path = os.path.join(os.getcwd(), 'web', 'chromedriver')

# Connect to db.
conn = db_connect('jobs.sqlite')
# Create table.
create_table(conn)
# Update db.
update_db(conn)
# Close connection to db.
conn.close()
