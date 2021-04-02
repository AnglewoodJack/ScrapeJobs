from db.clean_db import connect_pg, create_table_pg
from db.raw_db import connect_lite, create_table_lite
from core.update import update_db


def scrape():
    # Connect to db.
    conn = connect_lite('jobs.sqlite')
    # Create table.
    create_table_lite(conn)
    # Update db.
    update_db(conn)
    # Close connection to db.
    conn.close()
    print('Database connection closed.')


def transfer():
    # Connect to db.
    conn = connect_pg()
    # Create table.
    create_table_pg(conn)

    # Parse data from SQLite  DB and put them into PostgreSQL DB

    # Close connection to db.
    conn.close()
    print('Database connection closed.')


if __name__ == '__main__':
    scrape()
