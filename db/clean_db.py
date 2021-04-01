import os
import json
import psycopg2
from getpass import getpass


def pg_connect(pg_params_path):
    """

    """
    # Create connection object.
    conn = None
    # load db parameters
    with open(pg_params_path) as file:
        param = json.load(file)
        # ask user for password
        param['password'] = getpass()

    # Connect to db or create one if does not exist.
    try:
        conn = psycopg2.connect(**param)

    # Print error message if error.
    except psycopg2.Error as error:
        print(error)

    return conn


pg_connect("config.json")
