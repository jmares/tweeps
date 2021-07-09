from twitter import *
import sqlite3
from sqlite3 import Error
import sys
from config import *


def create_connection(db_file):
    """ 
    Create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def get_users(twit, type):
    """ Get list with user ids for Twitter friends or followers
    :param twit: Twitter connection
    :param type: Twitter user type (friends or followers)
    :return: list with ids
    """
    
    if type == 'friends':
        resp = twit.friends.ids(count=5000)
    elif type == 'followers':
        resp = twit.followers.ids(count=5000)
    else:
        raise Exception('Unknow Twitter user type. Valid types: friends and followers. Error type: ' + str(type))

    return resp['ids']


def update_followers(conn, twit):
    """
    Update Twitter followers' list: insert if new user and update when existing user
    :param conn: Database conection
    :param twit: Twitter connection
    :return: 
    """
    cur = conn.cursor()

    try:
        users = get_users(twit, 'followers')
    except Exception as e:
        print(e)
        sys.exit(1)

    print('\nStart followers\n')
    count = 0

    for id in users:
        # Test if the follower already exists
        sql_test = '''SELECT 1 FROM followers WHERE twitter_id = ?'''

        count += 1

        if cur.execute(sql_test, (id, )).fetchone():
            # print('update', str(id))
            sql = '''UPDATE followers SET last_date = datetime(CURRENT_TIMESTAMP, 'localtime') WHERE twitter_id = ?'''
            cur.execute(sql, (id, ))
        else:
            #print('insert', str(id))
            sql = '''INSERT INTO followers(twitter_id, start_date, last_date)
                VALUES(?, datetime(CURRENT_TIMESTAMP, 'localtime'), datetime(CURRENT_TIMESTAMP, 'localtime'))'''
            cur.execute(sql, (id, ))
        conn.commit()
    
    print('\nCount:' + str(count) + '\n')


def update_friends(conn, twit):
    """
    Update Twitter friends' list: insert if new user and update when existing user
    :param conn: Database conection
    :param twit: Twitter connection
    :return: 
    """
    cur = conn.cursor()

    try:
        users = get_users(twit, 'friends')
    except Exception as e:
        print(e)
        sys.exit(1)

    print('\nStart friends\n')
    count = 0

    for id in users:
        # Test if the follower already exists
        sql_test = '''SELECT 1 FROM friends WHERE twitter_id = ?'''

        count += 1

        if cur.execute(sql_test, (id, )).fetchone():
            # print('update', str(id))
            sql = '''UPDATE friends SET last_date = datetime(CURRENT_TIMESTAMP, 'localtime') WHERE twitter_id = ?'''
            cur.execute(sql, (id, ))
        else:
            # print('insert', str(id))
            sql = '''INSERT INTO friends(twitter_id, start_date, last_date)
                VALUES(?, datetime(CURRENT_TIMESTAMP, 'localtime'), datetime(CURRENT_TIMESTAMP, 'localtime'))'''
            cur.execute(sql, (id, ))
        conn.commit()

    print('\nCount:' + str(count) + '\n')


def get_meta_data_followers(conn, twit):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
    cur = conn.cursor()

    # Test if the follower already exists
    sql = '''SELECT twitter_id FROM followers WHERE screen_name IS NULL'''

    res = cur.execute(sql)
    for twitter_id, in res:
    #    print(twitter_id)
        try:
            user = twit.users.lookup(user_id=twitter_id)
            print(user[0]['id'], user[0]['screen_name'])
            add_meta_data_follower(conn, user[0])
        except TwitterHTTPError as err:
            print("Exceeded rate limit", err)
            break
        except Exception as e:
            print("Unknown error:", e)


def add_meta_data_follower(conn, user):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
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
    cur = conn.cursor()

    # Test if the follower already exists
    sql = '''SELECT twitter_id FROM friends WHERE screen_name IS NULL'''

    res = cur.execute(sql)
    for twitter_id, in res:
    #    print(twitter_id)
        try:
            user = twit.users.lookup(user_id=twitter_id)
            print(user[0]['id'], user[0]['screen_name'])
            add_meta_data_friend(conn, user[0])
        except TwitterHTTPError as err:
            print("Exceeded rate limit", err)
            break
        except Exception as e:
            print("Unknown error:", e)


def add_meta_data_friend(conn, user):
    """
    Create a new project into the vaccinations table
    :param conn:
    :param vacc:
    :return: row id
    """
    cur = conn.cursor()

    update = '''UPDATE friends SET screen_name = ? WHERE twitter_id = ?'''
    cur.execute(update, (user['screen_name'], user['id']))
    conn.commit()



def main():

    # create a database connection
    dbconn = create_connection(DB_FILE)
    
    twitconn = Twitter(auth=OAuth(TOKEN, TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

    print(type(dbconn))
    print(type(twitconn))

    update_followers(dbconn, twitconn)
    update_friends(dbconn, twitconn)
    get_meta_data_followers(dbconn, twitconn)
    get_meta_data_friends(dbconn, twitconn)

    #get_followers(conn, twit)
    
    #get_meta_data(conn, twit)

if __name__ == '__main__':
    main()
