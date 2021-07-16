from twitter import *
import sqlite3
from sqlite3 import Error
import sys
import os
from config import *
import logging
from datetime import datetime, date
#from time import time
import time

def create_connection(db_file):
    """ 
    Create a database connection to the SQLite database specified by db_file
    :param db_file: path to database file
    :return: Connection object or None
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug(this_function + ': start')
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        logging.debug(this_function + ': connected to database ' + db_file)
        return conn
    except Error as e:
        logging.critical(this_function + ': could not connect to database: ' + e)
        sys.exit(1)

    return conn


def get_users(twit, type):
    """ Get list with user ids for Twitter friends or followers
    :param twit: Twitter connection
    :param type: Twitter user type (friends or followers)
    :return: list with ids
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('get_users: ' + type)
    if type == 'friends':
        resp = twit.friends.ids(count=5000)
    elif type == 'followers':
        resp = twit.followers.ids(count=5000)
    else:
        logging.error('Unknow Twitter user type. Valid types: friends and followers. Error type: ' + str(type))
        raise Exception('Unknow Twitter user type. Valid types: friends and followers. Error type: ' + str(type))

    return resp['ids']


def update_followers(conn, twit):
    """
    Update Twitter followers' list: insert if new user and update when existing user
    :param conn: Database conection
    :param twit: Twitter connection
    :return: 
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('update_followers')
    cur = conn.cursor()

    try:
        users = get_users(twit, 'followers')
    except Exception as e:
        logging.error('update_followers: ' + e)
        sys.exit(1)

    count = 0

    for id in users:
        # Test if the follower already exists
        sql_test = '''SELECT 1 FROM followers WHERE twitter_id = ?'''

        count += 1

        if cur.execute(sql_test, (id, )).fetchone():
            logging.debug('update_followers: update ' + str(id))
            sql = '''UPDATE followers SET last_date = datetime(CURRENT_TIMESTAMP, 'localtime') WHERE twitter_id = ?'''
            cur.execute(sql, (id, ))
        else:
            logging.debug('update_followers: insert ' + str(id))
            sql = '''INSERT INTO followers(twitter_id, start_date, last_date)
                VALUES(?, datetime(CURRENT_TIMESTAMP, 'localtime'), datetime(CURRENT_TIMESTAMP, 'localtime'))'''
            cur.execute(sql, (id, ))
        conn.commit()
    
    logging.info('update_followers: ' + str(count) + ' followers')


def update_friends(conn, twit):
    """
    Update Twitter friends' list: insert if new user and update when existing user
    :param conn: Database conection
    :param twit: Twitter connection
    :return: 
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('update_friends')
    cur = conn.cursor()

    try:
        users = get_users(twit, 'friends')
    except Exception as e:
        logging.error('update_friends: ' + e)
        sys.exit(1)

    # print('\nStart friends\n')
    count = 0

    for id in users:
        # Test if the follower already exists
        sql_test = '''SELECT 1 FROM friends WHERE twitter_id = ?'''

        count += 1

        if cur.execute(sql_test, (id, )).fetchone():
            logging.debug('update_friends: update ' + str(id))
            sql = '''UPDATE friends SET last_date = datetime(CURRENT_TIMESTAMP, 'localtime') WHERE twitter_id = ?'''
            cur.execute(sql, (id, ))
        else:
            logging.debug('update_friends: update ' + str(id))
            sql = '''INSERT INTO friends(twitter_id, start_date, last_date)
                VALUES(?, datetime(CURRENT_TIMESTAMP, 'localtime'), datetime(CURRENT_TIMESTAMP, 'localtime'))'''
            cur.execute(sql, (id, ))
        conn.commit()

    logging.info('update_friends: ' + str(count) + ' friends')


def get_meta_data_followers(conn, twit):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('get_meta_data_followers')
    cur = conn.cursor()

    # Test if the follower already exists
    sql = '''SELECT twitter_id FROM followers WHERE screen_name IS NULL'''

    res = cur.execute(sql)
    for twitter_id, in res:
        try:
            user = twit.users.lookup(user_id=twitter_id)
            logging.debug('get_meta_data_followers: ' + str(user[0]['id']) + ' ' + user[0]['screen_name'])
            add_meta_data_follower(conn, user[0])
        except TwitterHTTPError as err:
            logging.error('get_meta_data_followers: exceeded rate limit - ' + err)
            break
        except Exception as e:
            logging.error('get_meta_data_followers: unknown error - ' + e)
            continue


def add_meta_data_follower(conn, user):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('add_meta_data_follower')
    cur = conn.cursor()

    update = '''UPDATE followers SET screen_name = ? WHERE twitter_id = ?'''
    cur.execute(update, (user['screen_name'], user['id']))
    conn.commit()


def get_meta_data_friends(conn, twit):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('get_meta_data_friends')
    cur = conn.cursor()

    # Test if the follower already exists
    sql = '''SELECT twitter_id FROM friends WHERE screen_name IS NULL'''

    res = cur.execute(sql)
    for twitter_id, in res:
        try:
            user = twit.users.lookup(user_id=twitter_id)
            logging.debug('get_meta_data_friends: ' + str(user[0]['id']) + ' ' + user[0]['screen_name'])
            add_meta_data_friend(conn, user[0])
        except TwitterHTTPError as err:
            logging.error('get_meta_data_friends: exceeded rate limit - ' + err)
            break
        except Exception as e:
            logging.error('get_meta_data_friends: unknown error - ' + e)
            continue


def add_meta_data_friend(conn, user):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
    this_function = sys._getframe().f_code.co_name
    logging.debug('add_meta_data_friend')
    cur = conn.cursor()

    update = '''UPDATE friends SET screen_name = ? WHERE twitter_id = ?'''
    cur.execute(update, (user['screen_name'], user['id']))
    conn.commit()


def get_log_file_mode(log_file):
    """
    Determine the file-mode for the log-file for weekday rotation
    :param log_file: path for the log-file
    :return: file-mode append or write, string
    """
    now = datetime.now()
    # check if log-file exists 
    if os.path.isfile(log_file):
        # if the log-file exists, compare the file modified date to the current date
        file_date = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(log_file)))
        if file_date == now.strftime("%Y-%m-%d"):
            # if the modified date of the log file equals the current date, set file-mode to append
            file_mode = 'a'
        else:
            # if the log-file is different (older), set file-mode to (over)write
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

    logging.info(this_function + ': start')

    # create a SQLite database connection
    try:
        dbconn = create_connection(DB_FILE)
    except Exception as e:
        logging.critical(this_function + ': could not connect to database: ' + e)
        sys.exit(1)
    
    # create a Twitter connection
    try:
        twitconn = Twitter(auth=OAuth(TOKEN, TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    except Exception as e:
        logging.critical(this_function + ': could not connect to Twitter: ' + e)
        sys.exit(1)

    #print(type(dbconn))
    #print(type(twitconn))

    update_followers(dbconn, twitconn)
    update_friends(dbconn, twitconn)
    get_meta_data_followers(dbconn, twitconn)
    get_meta_data_friends(dbconn, twitconn)

    #get_followers(conn, twit)
    
    #get_meta_data(conn, twit)
    end_time = time.time()
    duration = 'time needed for script: ' + str(round(end_time - start_time, 3)) + ' seconds\n\n'
    logging.info(duration)
    logging.debug('ending execution\n')

if __name__ == '__main__':
    main()
