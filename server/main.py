"""
Author: Ruben Rudov
Purpose: A local server for an android application that handles the connection to the mongodb database
"""
import socket
import threading
import smtplib
import json
from datetime import datetime
from pymongo import MongoClient

"""
Documentation for all the functions in this file: 
-------------

1) Functions in this file that operates on the database:
|
|--- Users collection:
|    add_new_user(username, email, password) -> inserts the username into the mongodb database. returns True 
     if successful else False.
|    get_account_password(username) -> returns the password for an account.
|    is_exist_element(value, key) -> returns True if the user/email is already in the users collection else returns False
|
|--- Posts collection: 
|    add_new_post(publisher, title, content, publishing_date) -> inserts the post into the mongodb database 
|    get_all_posts() -> returns a json object with all the posts found in the posts collections
|    exist_title(title) - > returns True if the post title is already exist else False

2) Other functions:
|--- main() -> calls all the functions
|--- connection_handling() -> adds new connection and handles it

About the database:
    I've used mongodb as my database for this project because I like working with NoSQL databases.
    This database is a json/document database that stored in cluster.
    The collections in the database are: users and posts. 
    To work with mongodb in python I've used the pymongo module (open source module that has to be installed with the pip)
    
Overview:
    Functions were written in name_of_function format.
    For string formatting I've used the f"Variable value: {variable}" format.
    The constant are used for database operations and communication.
    The protocol of the communication is TCP.
"""

# Server & communication constants setting
SERVER_IP = "0.0.0.0"
PORT = 8080
import string
DATABASE_CLUSTER = MongoClient(
    "mongodb://admin:G6HyJikC1wKwoz1c@main-cluster-shard-00-00.hukmn.mongodb.net:27017,main-cluster-shard-00-01.hukmn.mongodb.net:27017,main-cluster-shard-00-02.hukmn.mongodb.net:27017/<dbname>?ssl=true&replicaSet=atlas-rct4tj-shard-0&authSource=admin&retryWrites=true&w=majority")
DATABASE = DATABASE_CLUSTER["travmedia"]
USERS_COLLECTION = DATABASE["users"]
POSTS_COLLECTION = DATABASE["posts"]


# User collection related functions
def add_new_user(username: str, email: str, password: str):
    print(f"User data: {username}, {email}, {password}")
    post = {"username": username, "email": email, "password": password}

    if not is_exist_element(username, "username") or not is_exist_element(email, "email"):
        USERS_COLLECTION.insert_one(post)

    else:
        # TODO: Send a response via the socket for create a toast/alert dialog of "failed to register those values"
        print("Username or Email is already exist")

    return True


def get_account_password(username: str):
    search_results = USERS_COLLECTION.find({"username": username})
    print(search_results)

    for result in search_results:
        print(result)

    print(username)


def is_exist_element(value: str, key: str):
    print(f"value: {value} and {key} as key")

    if USERS_COLLECTION.find({key: value}):
        print("Exist")
        return True
    return False


# Posts collection related
def add_new_post(publisher: str, title: str, content: str, publishing_date: str):
    print(f"Post data: {publisher}, {title}, {content} {publishing_date}")
    post = {"publisher": publisher, "title": title, "content": content, "publishing_date": publishing_date}

    if not exist_title(title):
        POSTS_COLLECTION.insert_one(post)

    else:
        # TODO: Send a response via the socket for create a toast/alert dialog of "Post title is already exist"
        print("Post title is already exist")


def get_all_posts():
    all_posts = POSTS_COLLECTION.find({})  # gets all the posts
    return all_posts


def exist_title(title: str):
    if USERS_COLLECTION.find({"title": title}):
        return True
    return False


# Connection & communication handling
def connection_handling():
    return None


def main():
    # testing user
    username = "rubenrudov"
    email = "rudovruben4all@gmail.com"
    password = "12345678"
    add_new_user(username=username, email=email, password=password)
    users = USERS_COLLECTION.find({})

    for user in users:
        print(user)

    # testing post
    publisher = username
    title = "About my trip to the golan heights"
    content = ""
    publishing_date = datetime.now().__format__("%d/%m/%Y %H:%M:%S")
    add_new_post(publisher=publisher, title=title, content=content, publishing_date=publishing_date)
    posts = get_all_posts()

    for post in posts:
        print(post)


if __name__ == "__main__":
    main()
