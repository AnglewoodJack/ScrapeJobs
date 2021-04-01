from db.raw_db import db_connect, create_table
from core.update import update_db


if __name__ == '__main__':
    # Connect to db.
    conn = db_connect('jobs.sqlite')
    # Create table.
    create_table(conn)
    # Update db.
    update_db(conn)
    # Close connection to db.
    conn.close()
