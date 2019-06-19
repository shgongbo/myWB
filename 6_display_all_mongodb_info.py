import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import pymongo

def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['choujiang']
    collection = mongodb[collection_name]
    return collection

seperate_list = [0, 100, 200, 400, 600, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
                              15000, 20000, 30000, 50000, 100000, 200000, 500000, 1000000, 1000000000]

total = 0
more_than_10000 = 0
more_than_5000 = 0
for seperate_index in range(1, len(seperate_list)):
    start = seperate_list[seperate_index - 1]
    end = seperate_list[seperate_index]
    mongo_db = get_mongo("%s_%s" % (start, end)).count_documents({})
    print("%s_%s has %s" % (start, end,mongo_db))
    total += mongo_db
    if start >= 10000:
        more_than_10000 += mongo_db
    if start >= 5000:
        more_than_5000 += mongo_db
print("now total is %s " % total)
print("more than 10000 is %s" % more_than_10000)
print("more than 5000 is %s" % more_than_5000)
print("now base has %s" % (get_mongo("base_users").count_documents({})))
print("all links number is %s" % (get_mongo("all_links_mongo").count_documents({})))
print("all not used links number is %s" % (get_mongo("all_links_mongo").count_documents({"tag":0})))
print("useful links number is %s" % (get_mongo("useful_links_mongo").count_documents({})))
print("useful not used links number is %s" % (get_mongo("useful_links_mongo").count_documents({"tag":0})))

