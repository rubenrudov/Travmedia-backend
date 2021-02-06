# Imports for MongoDB relevant modules
import pymongo
from pymongo import MongoClient

# Cluster setting
cluster = MongoClient("mongodb://admin:G6HyJikC1wKwoz1c@main-cluster-shard-00-00.hukmn.mongodb.net:27017,main-cluster-shard-00-01.hukmn.mongodb.net:27017,main-cluster-shard-00-02.hukmn.mongodb.net:27017/<dbname>?ssl=true&replicaSet=atlas-rct4tj-shard-0&authSource=admin&retryWrites=true&w=majority")

# Database setting
database = cluster["test"]

# Relevant collections list setting

collection = database["test"]

# Data form:
post = {"_id": 0, "username": "Ruben", "password": "12345678"}  # Manual ID
post2 = {"username": "Rudov", "password": "87654321"}           # Random ID

# Insert one value into the database collection
# collection.insert_one(post)

# Insert multiple values:
collection.insert_many([post, post2])

# Read data:
result_sets = collection.find({})
print(result_sets)

for result_set in result_sets:
    print(result_set)

# Update commands
collection.update_one({"_id": 0}, {"$set": {"username": "Ruby"}})  # search query and preferred values updating


result_sets = collection.find({})
print(result_sets)

for result_set in result_sets:
    print(result_set)

# Delete commands:
# collection.delete_many([post, post]) Gets a list of objects to remove
