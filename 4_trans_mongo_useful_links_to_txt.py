
import pymongo
import config

import os


def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['choujiang']
    collection = mongodb[collection_name]
    return collection
# get_mongo("all_links_mongo").update_many({},{"$set":{"tag":0}})
# get_mongo("useful_links_mongo").update_many({},{"$set":{"tag":0}})
# get_mongo("useful_ids").update_many({},{"$set":{"tag":0}})
# exit(0)
useful_links_mongo = get_mongo("useful_links_mongo")
if os.path.exists("useful_links.txt"):
    os.remove("useful_links.txt")
# exit(0)
with open("useful_links.txt","a") as file:
    useful_links = useful_links_mongo.find({"tag":0})
    for useful_link in useful_links:
        file.write(useful_link["url"])
        file.write("\n")
        useful_links_mongo.update_one({"_id":useful_link["_id"]},{"$set":{"tag":1}})
