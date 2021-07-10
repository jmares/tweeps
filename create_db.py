import sqlite3
from sqlite3 import Error
from config import DB_FILE


def create_connection(db_file):
    """Create a database connection to the SQLite database

    :param db_file: path to database file, string
    :return: SQLite3 Connection or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_table(conn, ddl_sql):
    """Create a table from a given DDL statement

    :param conn: SQLite3 Connection
    :param ddl_sql: a CREATE TABLE statement, string
    :return: Boolean
    """
    try:
        c = conn.cursor()
        c.execute(ddl_sql)
    except Error as e:
        print(e)
        return False
    return True


def main():
    """Create database with two tables """

    sql_create_followers = """CREATE TABLE IF NOT EXISTS followers(
        twitter_id INTEGER PRIMARY KEY,
        screen_name TEXT UNIQUE,
        start_date TEXT NOT NULL, 
        last_date TEXT NOT NULL
    ); """

    sql_create_friends = """CREATE TABLE IF NOT EXISTS friends(
        twitter_id INTEGER PRIMARY KEY,
        screen_name TEXT UNIQUE,
        start_date TEXT NOT NULL, 
        last_date TEXT NOT NULL
    ); """

    # create a database connection
    conn = create_connection(DB_FILE)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_followers)
        create_table(conn, sql_create_friends)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()