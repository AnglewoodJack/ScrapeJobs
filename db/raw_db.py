import os
import sqlite3

from tqdm import tqdm
from time import sleep


def db_connect(db_filename):
    """
    Connects to SQLite database file "db_filename".
    If does not exist, creates new database file.
    :param db_filename: database file name.
    :return: db connection object.
    """
    # Create connection object.
    conn = None

    # Connect to db or create one if does not exist.
    try:
        conn = sqlite3.connect(
            os.path.join(
                os.path.dirname(__file__), db_filename
            )
        )

    # Print error message if error.
    except sqlite3.Error as error:
        print(error)

    return conn


def create_table(conn):
    """
    Creates table if not exist.
        id - primary key;
        job_id - unique job identifier;
        title - job title;
        location - job location;
        deadline - application deadline;
        organization - IAEA, ITER, IRENA or OECD;
        html - source code of job's web page;
        reopen - 1 if vacancy is re-opened, 0 otherwise.
    :params conn: db connection object.
    """
    # Create cursor.
    cur = conn.cursor()
    # Create table.
    query = """CREATE TABLE IF NOT EXISTS vacancies (id INTEGER PRIMARY KEY, job_id TEXT, title TEXT, location TEXT,
            deadline DATETIME, organization TEXT, html TEXT, reopen INTEGER, UNIQUE(job_id, deadline));
            """
    cur.execute(query)
    conn.commit()


def add_vacancies(vacancies: list, conn):
    """
    Add vacancies into database table.
    :param vacancies: list of dictionaries with jobs info.
    :param conn: db connection object.
    """
    # Get jobs list organization name.
    org = vacancies[0]['organization']
    # Create cursor.
    cur = conn.cursor()
    # Iterate over vacancies.
    for job in tqdm(vacancies, desc=f"Inserting {org}'s jobs info"):
        insert_query = """
        INSERT OR IGNORE INTO vacancies (job_id, title, location, deadline, organization, html, reopen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(
            insert_query,
            (
                job['id'],
                job['title'],
                job['location'],
                job['deadline'],
                job['organization'],
                job['html_page'],
                job['reopen']
            )
        )
        sleep(0.3)
    # Apply insertion.
    conn.commit()
    print("Insertion completed.")


def get_vacancies(conn, full=False):
    """
    Retrieves list of jobs from db.
    :param conn: db connection object.
    :param full: if True retrieves full information about vacancies,
    otherwise gets "organization", "title" and "deadline".
    :return: list with query results.
    """
    # Create cursor.
    cur = conn.cursor()
    # Query for the information to retrieve from db.
    if full:
        query = "SELECT job_id, title, location, deadline, organization, html, reopen FROM vacancies;"
    else:
        query = "SELECT organization, title, deadline FROM vacancies;"

    # Execute query and get all results.
    cur.execute(query)
    rows = cur.fetchall()

    return rows
