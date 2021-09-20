# Tweeps

Keeping track of my Twitter followers and friends

About the `.keep` files: **git** doesn't commit empty folders, so when I want an empty folder to be commited to **GitHub** I add an empty file to the folder.

## Goal

The goal of this app is to answer some questions about my *tweeps*. There are ready-made solutions available, but I wanted to build one myself to practise **python** and **sql**.

The question I try to answer in v0.10 is who are the people who unfollow me? 

I have no intention of contacting those people. You are free to follow or unfollow me at your leisure. However, I cannot help but wonder who the people are that unfollowed me and why. Were they long-time followers or recent ones? I tweet about several topics. What do or did we have in common? Did I tweet too much or not enough about a certain topic?

I hope this might shed some light on those questions.

## Twitter

You can get access to the Twitter API for free, rate limited, but you have to register as a developer.

- [Twitter Developer Platform](https://developer.twitter.com/en)

After you have registered, go to the developer portal and create a standalone app. You will need the following information to access the Twitter API with your app:

- Access Token
- Access Secret
- API Key
- API Secret

This information needs to be included in the `config.py`. How? Copy the `config-sample.py` and fill in the values.

## Database

As this is a small project it requires only a small database, and for this SQLite is the ideal solution.

The databases contains two tables, which are identical except for the name: *friends* and *followers*.

According to Twitter: a friend is someone you follow and a follower is someone who follows you.

Why do I use two tables if they are identical? A one-table solution is a possibility. However, using two tables seems like a good excuse to practise left and right (outer) joins. Who follows me that I don't follow back and vice-versa.

The CREATE statements for the two table:

```sql
CREATE TABLE IF NOT EXISTS followers(
    twitter_id INTEGER PRIMARY KEY,
    screen_name TEXT UNIQUE,
    start_date TEXT NOT NULL, 
    last_date TEXT NOT NULL
);
```

```sql
CREATE TABLE IF NOT EXISTS friends(
    twitter_id INTEGER PRIMARY KEY,
    screen_name TEXT UNIQUE,
    start_date TEXT NOT NULL, 
    last_date TEXT NOT NULL
);
```

Attributes/fields/columns:

- twitter_id: the unique id for an account as assigned by Twitter
- screen_name: the screen-name a person uses on Twitter
- start_date: the date I started following someone, the date a person started following me, or the first time this script ran
- last_date: the last time that this person was found to be a follower and/or a friend

The script `create_db.py` will create the database with the two tables for you. It requires a writable `db` folder in the current directory.

## Twitter

## Importing the Data

## Using the Data


## Logging

Each function starts with the statement:

```python
this_function = sys._getframe().f_code.co_name
```

This stores the name of the current function in the variable `this_function`.    
Why not just type the name of the function, eg. `this_function = "main"`? If I merge 2 functions, split a function, or rename a function, I will have to manually verify that all the `this_function` variables have the correct value, wich isn't the case when I assign it the value derived from `sys._getframe().f_code.co_name`.

