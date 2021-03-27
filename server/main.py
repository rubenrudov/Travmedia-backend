"""
Author: Ruben Rudov
Purpose: A local server for an android application that handles the connection to the mongodb database
"""

import socket
import threading
import json
from pymongo import MongoClient
from server.mail_sending import MailHandler

# Server & communication constants setting
SERVER_SOCKET_AUTH = ("0.0.0.0", 6000)
DATABASE_CLUSTER = MongoClient(
    "mongodb://admin:G6HyJikC1wKwoz1c@main-cluster-shard-00-00.hukmn.mongodb.net:27017,main-cluster-shard-00-01.hukmn.mongodb.net:27017,main-cluster-shard-00-02.hukmn.mongodb.net:27017/<dbname>?ssl=true&replicaSet=atlas-rct4tj-shard-0&authSource=admin&retryWrites=true&w=majority")
DATABASE = DATABASE_CLUSTER["travmedia"]
USERS_COLLECTION = DATABASE["users"]
POSTS_COLLECTION = DATABASE["posts"]


# User collection related functions
def add_new_user(username: str, email: str, password: str):
    """
    :param username: string that contains the username
    :param email: string that contains the email
    :param password: string that contains the password
    :return: bool that represents the result of the insert to the database (successful -> True, unsuccessful -> False)
    """
    print(f"User data: {username}, {email}, {password}")
    post = {"username": username, "email": email, "password": password}

    if not is_exist_element(username, "username") or not is_exist_element(email, "email"):
        USERS_COLLECTION.insert_one(post)

        mail_sender = MailHandler(email_to=email, username=username)
        mail_sender.send_email()
        del mail_sender

        return True

    print("Debug: username or Email is already exist")
    return False


def get_account_password(username: str):
    """
    :param username: string that represents the username
    :return: the password of the specific username in the database
    """
    search_results = USERS_COLLECTION.find({"username": username})
    for search_result in search_results:
        return search_result["password"]

    return search_results


def is_exist_element(value: str, key: str):
    """
    :param value: string that contains a value
    :param key: string that contains the searching key {key: value}
    :return: if exist -> True else -> False
    """
    print(f"value: {value} and {key} as key")

    if USERS_COLLECTION.find({key: value}) is {}:
        print("Exist")
        return True

    return False


# Posts collection related
def add_new_post(publisher: str, title: str, content: str, publishing_date: str):
    """
    :param publisher: string that contains the username of the post publisher
    :param title: string that contains the post title
    :param content: string that contains the post content
    :param publishing_date: string that contains the post publishing date and time
    :return:
    """
    _id = POSTS_COLLECTION.count() + 1     # The id of the next

    post = {"_id": _id, "publisher": publisher, "title": title, "content": content,
            "publishing_date": publishing_date}

    if not exist_title(title):
        POSTS_COLLECTION.insert_one(post)

        # For debugging, check if the value was inserted
        mongo_cursor_result = POSTS_COLLECTION.find({"_id": _id})
        for item in mongo_cursor_result:
            print(item)
        return True

    print("Debug: post title is already exist")
    return False


def get_all_posts():
    """
    :return: a json of all the posts found in the POST_COLLECTION of the database
    """
    all_data = {}  # Data to send
    __key = 0       # "Private key"
    mongo_cursor_result = POSTS_COLLECTION.find({})    # Running a searching query for mongo
    value = mongo_cursor_result[__key]
    print(value)
    print(type(value))  # still a dict
    print(type(json.dumps(value)))      # str

    while value is not None:
        all_data[__key] = value

    return all_data


def get_post(title):
    """
    Function for search the first post with the keyword
    :param title: str
    :return: dict
    """
    for item in range(len((list(POSTS_COLLECTION.find({}))))):
        print(item)
        if title in list(POSTS_COLLECTION.find({}))[item]['title']:
            print(title)
            return list(POSTS_COLLECTION.find({}))[item]


def exist_title(title: str):
    """
    :param title: string that contains the post title
    :return: if exist -> True, else -> False
    """
    if POSTS_COLLECTION.find({"title": title}) is {}:
        print("Exist")
        return True

    return False


# Connection & communication handling
def request_handling(client_socket: socket.socket, data_struct):
    """
    :param client_socket: a connection socket between the client to the server
    :param data_struct: a json that contains the request and other params that matches the request
    :return: None
    """
    if data_struct["request"] == "add_user":
        response = add_new_user(
            data_struct["username"],
            data_struct["email"],
            data_struct["password"],
        )

        if response is True:
            data = {"response": "Successful"}

        else:
            data = {"response": "Unsuccessful"}

        client_socket.send(json.dumps(data).encode())

    elif data_struct["request"] == "get_password":
        password = get_account_password(data_struct["username"])
        data = {"response": f"{password}"}
        client_socket.send(json.dumps(data).encode())

    elif data_struct["request"] == "add_post":
        print(data_struct["request"])
        response = add_new_post(
            data_struct["username"],
            data_struct["title"],
            data_struct["content"],
            data_struct["publishing_date"],
        )

        if response is True:
            data = {"response": "Successful"}

        else:
            data = {"response": "Unsuccessful"}
        client_socket.send(json.dumps(data).encode())

    elif data_struct["request"] == "get_all_posts":
        # TODO: Implement getting in the app
        data = get_all_posts()
        # for data_piece in data.items():
        #     sending = {"response": data_piece[1]}
        #     client_socket.send(json.dumps(sending).encode())

    elif data_struct["request"] == "get_post":
        data = data_struct["keyword"]
        found = get_post(data)
        if found:
            response = {
                "response": "OK",
                "publisher": found['publisher'],
                "title": found['title'],
                "content": found['content'],
                "publishing_date": found['publishing_date']
            }
            client_socket.send(json.dumps(response).encode())
        else:
            response = {
                "response": "NOT OK"
            }
            client_socket.send(json.dumps(response).encode())

    else:
        client_socket.send(json.dumps({"response": "Unknown command, Debug mode..."}))


def new_connection(client_socket: socket.socket, ip_address: str):
    """
    :param client_socket: a connection socket between the client to the server
    :param ip_address: a string that represents an ip address
    :return: a dictionary
    """
    print(f"Debug: {ip_address} has connected to the server via {client_socket}")
    data = client_socket.recv(1024)
    decoded_data = data.decode()
    data_struct = json.loads(decoded_data)
    request_handling(client_socket, data_struct)
    client_socket.close()
    return data_struct


def main():
    """
    The main function of the server, which controls the connections receiving with threading
    :return: None
    """
    print("Server is up now")
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
