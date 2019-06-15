"""
这个代码是需要登陆之后使用的，需要配置对应的账号信息才能使用
"""

import requests
import re
import pymongo
import threading
import redis
import queue
import tools
import time
import json
import socket
import config


class UserCrawler(object):
    def __init__(self):
        self.start_point = 3000000
        self.mongo = self.get_mongo("users_id")
        self.mongo.create_index("id", unique=True)
        self.sem1 = threading.BoundedSemaphore(20)
        self.sem2 = threading.BoundedSemaphore(20)
        self.old = 0
        self.new = 0
        self.queue = queue.Queue(10000)
        self.proxy_redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
        self.base_url = "https://weibo.com/u/"
        self.now_mongo_point = self.mongo.count_documents({})
        if self.now_mongo_point == 0:
            self.mongo.insert_one({
                "_id": 0,
                "id": "6190467306",
                "tag": 0
            })
            self.now_mongo_point = 1
        else:
            temp = self.mongo.find().sort("_id",-1)
            for i in temp:
                self.now_mongo_point = i["_id"] + 1
                break
        self.lock = threading.Lock()

    def get_mongo(self, collection_name):
        client = pymongo.MongoClient(config.MONGO_URL)
        mongodb = client['weibo']
        collection = mongodb[collection_name]
        return collection

    def save_to_mongo(self, user_id):
        try:
            self.mongo.insert_one({
                "_id": self.now_mongo_point,
                "id": user_id,
                "tag": 0
            })
        except Exception as e:
            return
        self.lock.acquire()
        self.now_mongo_point += 1
        self.lock.release()

    def parse_page(self, url, id):
        times = 0
        while True:
            try:
                page = requests.post(tools.base_url, json={"url": url, "headers": tools.headers})
            except Exception as e:
                times += 1
                if times > 10:
                    self.sem1.release()
                    print("2")
                    print(e)
                    return
                continue

            page = json.loads(page.text)
            if page["type"] =="error":
                times += 1
                if times > 10:
                    self.sem1.release()
                    print("2")
                    print(page["text"])
                    return
                continue
            else:
                break
        page = page["text"]
        user_fans_and_follows_pattenr = re.compile("page_id']='([\d]+?)'")
        user_fans_and_follows = user_fans_and_follows_pattenr.findall(page)
        if len(user_fans_and_follows) != 1:
            print("Failed: user_id is %s" % id)
            try:
                print(page)
            except Exception as e:
                pass

            self.sem1.release()
            return
        else:
            print("--" * 10)
        for i in range(1, 6):
            self.queue.put("https://weibo.com/p/%s/follow?relate=fans&page=%s#Pl_Official_HisRelation__59" % (
            user_fans_and_follows[0], i))
            self.queue.put(
                "https://weibo.com/p/%s/follow?page=%s#Pl_Official_HisRelation__59" % (user_fans_and_follows[0], i))
        self.sem1.release()

    def parse_fans_and_follows(self, url):
        try:
            page = requests.post(tools.base_url,
                          json={"url": url, "headers": tools.headers})
        except Exception as e:
            self.sem2.release()
            return

        page = json.loads(page.text)
        if page["type"] == "error":
            self.sem2.release()
            return
        page = page["text"]
        fans_pattern = re.compile("fanslist&uid=([\d]+?)&fnick")
        follows_pattern = re.compile("followlist&uid=([\d]+?)&fnick")
        fans_list = fans_pattern.findall(page)
        follows_list = follows_pattern.findall(page)
        for fans in fans_list:
            self.save_to_mongo(fans)
        for follow in follows_list:
            self.save_to_mongo(follow)
        if len(follows_list) + len(fans_list) == 0:
            # print("Failed %s " % url)
            pass
        self.sem2.release()

    def find_fans_and_follows(self):
        while True:
            url = self.queue.get()
            self.sem2.acquire()
            t = threading.Thread(target=self.parse_fans_and_follows, args=(url,))
            t.start()

    def crawler(self):
        t = threading.Thread(target=self.find_fans_and_follows)
        t.start()
        tsk = []
        start_num = 0
        while True:
            time.sleep(1)
            while self.start_point < self.now_mongo_point:
                print("time %s start point is %s, now point is %s" % (time.strftime("%Y/%m/%d  %H:%M:%S"),
                    self.start_point, self.now_mongo_point))
                data = self.mongo.find_one({"_id": self.start_point})
                self.start_point += 1
                if data is None:
                    continue

                self.sem1.acquire()
                t = threading.Thread(target=self.parse_page, args=(self.base_url + data["id"], data["id"]))
                tsk.append(t)
                t.start()
                start_num += 1


if __name__ == "__main__":
    userCrawler = UserCrawler()
    userCrawler.crawler()
