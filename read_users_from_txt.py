import pymongo
import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config

def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['choujiang']
    collection = mongodb[collection_name]
    return collection

user_mongo = get_mongo("base_users")
users = user_mongo.find()
with open("users.txt","r") as file:
    num = 0
    for line in file:
        print(num)
        num+=1
        user_mongo.insert_one({
            "id":line.rstrip("\n"),
            "tag":0
        })