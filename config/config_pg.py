from pathlib import Path
from configparser import ConfigParser


def config(directory=Path.cwd().parent, section='postgresql'):
    """
    Configure PostgreSQL connection.
    :param directory: path to parent directory for database parameters ".ini" file
    :param section: database section name.
    :return: database parameters dictionary.
    """
    # find database.ini file (given parent directory for current file)
    ini_files = directory.glob('**/*.ini')
    files = [x for x in ini_files if x.is_file()]
    # define valid path
    if len(files) > 1:
        file_path = input("More than 1 '.ini file found. Please, specify path to valid database parameters file: ")
    elif len(files) == 0:
        file_path = input("'.ini file not found. Please, specify path to valid database parameters file: ")
    else:
        file_path = files[0]

    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(file_path)

    # get section, default to postgresql
    db = {}
    # get db params
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, file_path))

    return db
