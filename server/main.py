"""
Author: Ruben Rudov
Purpose: A local server for an android application that handles the connection to the mongodb database
"""

import socket
import threading
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
SERVER_SOCKET_AUTH = ("0.0.0.0", 8080)
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
        return True

    print("Debug: username or Email is already exist")
    return False


def get_account_password(username: str):
    search_results = USERS_COLLECTION.find({"username": username}["password"])
    print(f"Debug: {search_results}")

    return search_results


def is_exist_element(value: str, key: str):
    print(f"value: {value} and {key} as key")

    if USERS_COLLECTION.find({key: value}) is {}:
        print("Exist")
        return True
    return False


# Posts collection related
def add_new_post(publisher: str, title: str, content: str, publishing_date: str):
    print(f"Post data: {publisher}, {title}, {content} {publishing_date}")
    post = {"publisher": publisher, "title": title, "content": content, "publishing_date": publishing_date}

    if not exist_title(title):
        POSTS_COLLECTION.insert_one(post)
        return True

    print("Debug: post title is already exist")
    return False


def get_all_posts():
    all_posts = POSTS_COLLECTION.find({})  # gets all the posts
    return all_posts


def exist_title(title: str):
    if USERS_COLLECTION.find({"title": title}):
        return True
    return False


# Connection & communication handling
def connection_request_handling(client_socket: socket.socket, data_struct: json):
    if data_struct["request"] == "add_user":
        response = add_new_user(
            data_struct["username"],
            data_struct["email"],
            data_struct["password"],
        )

        if response is True:
            return "Done"   # TODO: Transport the data by the client socket to the client

        else:
            return "Failed"

    elif data_struct["request"] == "get_password":
        password = get_account_password(data_struct["username"])
        return password

    elif data_struct["request"] == "add_post":
        response = add_new_post(
            data_struct["publisher"],
            data_struct["title"],
            data_struct["content"],
            data_struct["publishing_date"],
        )

        if response is True:
            return "Done"  # TODO: Transport the data by the client socket to the client

        else:
            return "Failed"

    elif data_struct["request"] == "get_all_posts":
        all_posts = get_all_posts()
        return json.load(all_posts)     # TODO: Transport the data by the client socket to the client

    else:
        print("Unknown request")       # TODO: Send an "unknown request" message to the user


def new_connection(client_socket: socket.socket, ip_address: str):
    print(f"Debug: {ip_address} has connected to the server via {client_socket}")
    data = client_socket.recv(1024).decode('UTF-8')
    data_struct = json.load(data)
    connection_request_handling(client_socket, data_struct)
    return data_struct


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_SOCKET_AUTH)
    server_socket.listen()  # Listens for unlimited amount of clients

    while True:
        new_client = server_socket.accept()
        new_client_thread = threading.Thread(target=new_connection, args=new_client)

        new_client_thread.start()
        print(f"{new_client}'s thread is now on")


if __name__ == "__main__":
    main()
