import psycopg2
from config.config_pg import config


def connect_pg():
    """
    Connect to the PostgreSQL database server.
    """
    # Create connection object.
    conn = None

    # Connect to db.
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        # close the communication with the PostgreSQL
        cur.close()

    # Print error message if error.
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return conn


def create_table_pg(conn):
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


