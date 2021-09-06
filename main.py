from twitter import *
import sqlite3
from sqlite3 import Error
import sys
import os
from config import *
import logging
from datetime import datetime
import time

def create_dbconnection(db_file):
    """ 
    Create a database connection to the SQLite database specified by db_file
    :param db_file: path to database file
    :return: SQLite3 connection or None
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(f"{this_function}: start")
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        logging.debug(f"{this_function}: connected to database {db_file}")
        return conn
    except Error as e:
        logging.critical(f"{this_function}: could not connect to database - {e}")
        sys.exit(1)

    return conn


def get_users(twitcon, user_type):
    """ 
    Get list with user ids for Twitter friends or followers
    :param twitcon: Twitter connection
    :param user_type: Twitter user type (friends or followers)
    :return: list with Twitter ids
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(f"{this_function} - {user_type}")

    if user_type == 'friends':
        resp = twitcon.friends.ids(count=5000)
    elif user_type == 'followers':
        resp = twitcon.followers.ids(count=5000)
    else:
        msg = f"Unknow Twitter user type: {str(user_type)}. Valid types: friends and followers."
        logging.error(msg)
        raise Exception(msg)

    return resp['ids']


def update_users(dbcon, twitcon, user_type):
    """
    Update Twitter users list: insert if new user and update when existing user
    :param dbcon: Database connection
    :param twitcon: Twitter connection
    :param user_type: User type (friends or followers), specifies table in database
    :return: 
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(f"{this_function} - {user_type}")
    cur = dbcon.cursor()

    try:
        users = get_users(twitcon, user_type)
    except Exception as e:
        logging.error(f"{this_function} - {user_type}: {e}")
        sys.exit(1)

    count = 0

    for id in users:
        # Test if the follower already exists
        sql_test = f'''SELECT 1 FROM {user_type} WHERE twitter_id = ?'''
        count += 1

        if cur.execute(sql_test, (id, )).fetchone():
            logging.debug(f"{this_function} {user_type}: update id {str(id)}")
            sql = f'''UPDATE {user_type} 
                SET last_date = datetime(CURRENT_TIMESTAMP, 'localtime') 
                WHERE twitter_id = ?'''
            cur.execute(sql, (id, ))
        else:
            logging.debug(f"{this_function} {user_type}: insert id {str(id)}")
            sql = f'''INSERT INTO {user_type} (twitter_id, start_date, last_date)
                VALUES(?, datetime(CURRENT_TIMESTAMP, 'localtime'), 
                datetime(CURRENT_TIMESTAMP, 'localtime'))'''
            cur.execute(sql, (id, ))

        dbcon.commit()
    
    logging.info(f"{this_function}: {str(count)} {user_type}")


def get_metadata_users(dbcon, twitcon, user_type):
    """
    Get metadata for the users with missing metadata
    :param dbcon: Database connection
    :param twitcon: Twitter connection
    :param user_type: User type (friends or followers)
    :return: 
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(f"{this_function} - {user_type}")
    cur = dbcon.cursor()

    # Get users with missing metadata (currently only screen-name)
    sql = f'''SELECT twitter_id FROM {user_type} WHERE screen_name IS NULL'''

    res = cur.execute(sql)
    for twitter_id, in res:
        try:
            user = twitcon.users.lookup(user_id=twitter_id)
            logging.debug(f"{this_function} - {user_type}: {str(user[0]['id'])} {user[0]['screen_name']}")
            add_metadata_user(dbcon, user[0], user_type)
        except TwitterHTTPError as e:
            logging.error(f"{this_function} - {user_type}: exceeded rate limit {e}")
            break
        except Exception as e:
            logging.error(f"{this_function} - {user_type}: unexpected error {e}")
            continue


def add_metadata_user(dbcon, user, user_type):
    """
    Add metadata for a specific user (currently only screenname)
    :param dbcon: Database connection
    :param user: dictionary with user metadata
    :param user_type: User type (friends or followers)
    :return: 
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(f"{this_function} - {user_type}")
    cur = dbcon.cursor()

    update = f'''UPDATE {user_type} SET screen_name = ? WHERE twitter_id = ?'''
    logging.debug(f"{this_function} - {user_type}: {str(user['id'])} {user['screen_name']}")
    cur.execute(update, (user['screen_name'], user['id']))
    dbcon.commit()


def get_log_file_mode(log_file):
    """
    Determine the file-mode for the log-file for weekday rotation
    :param log_file: path for the log-file
    :return: file-mode append or write, string
    """
    now = datetime.now()
    # check if log-file exists 
    if os.path.isfile(log_file):
        # if the log-file exists, compare the modified date to the current date
        file_date = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(log_file)))
        if file_date == now.strftime("%Y-%m-%d"):
            # if the modified date equals the current date, set file-mode to append
            file_mode = 'a'
        else:
            # if the modified date is different (older), set file-mode to (over)write
            file_mode = 'w'
    else:
        # if the log-file doesn't exist, set file-mode to write
        file_mode = 'w'

    return file_mode


def main():

    this_function = sys._getframe().f_code.co_name
    start_time = time.time()
    now = datetime.now()
    # create log-file per weekday: tweeps_Wed.log
    log_file = LOG_DIR + 'tweeps_' + now.strftime('%a') + '.log'
    log_level = logging.INFO

    file_mode = get_log_file_mode(log_file)
    logging.basicConfig(filename=log_file, filemode=file_mode, format='%(asctime)s - %(levelname)s : %(message)s', level=log_level)

    logging.info(f"{this_function}: start")

    # create a SQLite database connection
    try:
        dbconn = create_dbconnection(DB_FILE)
    except Exception as e:
        logging.critical(f"{this_function}: could not connect to database: {e}")
        sys.exit(1)
    
    # create a Twitter connection
    try:
        twitconn = Twitter(auth=OAuth(TOKEN, TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    except Exception as e:
        logging.critical(f"{this_function}: could not connect to Twitter: {e}" )
        sys.exit(1)

    update_users(dbconn, twitconn, 'followers')
    update_users(dbconn, twitconn, 'friends')
    get_metadata_users(dbconn, twitconn, 'followers')
    get_metadata_users(dbconn, twitconn, 'friends')

    end_time = time.time()
    duration = str(round(end_time - start_time, 3))
    logging.info(f"{this_function}: time needed for script {duration} seconds\n")
    logging.debug(f"{this_function}: ending execution\n")


if __name__ == '__main__':
    main()
