"""
把用户分为值得关注的和不值得关注的

每当来了新的一批账号，把新的账号存在base_users这个表中，然后先把当前的有用的和无用的账号和这批账号合并，把以前做的有用的和无用的账号的分类删除（因为数据可能比较旧了）
然后对这个合并之后的账号集合进行清洗

这个程序不用经常跑，一个月一次都是ok的
"""

import re
import requests
import pymongo
import config
import tools
import threading
import json


class SeperateUsers(object):
    def __init__(self):
        self.headers = {
            "Host": "weibo.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
            "Cookie": "SINAGLOBAL=1971032401731.4163.1551954096720; un=15110248779; SCF=AkxnN3UOg2_gI0lQpJs3Ce5OGPpjj6UqYzvn1zDxH3Uwl3b35CjAtVKOURGjNAkkh-iPd3fV3KdOrDRqiumv8x8.; SUHB=0wn1jo3H0zlFQX; webim_unReadCount=%7B%22time%22%3A1560429869784%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A2%2C%22msgbox%22%3A0%7D; SUB=_2AkMqXsoLdcPxrAZVm_0QzmLraotH-jyZi6P9An7uJhMyAxgv7nBXqSVutBF-XFJVO0gHZ69gfDqyu-jJLhcZggAo; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhQlbikHdp9PNYWkFUk2aa35JpVF02feK27eoBRS0M4; UOR=,,www.baidu.com; login_sid_t=08427fb0fafd381ee7671d7b96f4112e; cross_origin_proto=SSL; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; _s_tentry=www.baidu.com; wb_view_log=1920*10801; YF-V5-G0=27518b2dd3c605fe277ffc0b4f0575b3; WBStorage=6b696629409558bc|undefined; Apache=4050300198651.866.1560477141158; ULV=1560477141176:3:3:3:4050300198651.866.1560477141158:1560432380350; YF-Page-G0=afcf131cd4181c1cbdb744cd27663d8d|1560477144|1560477144"
        }
        self.useful_mongo = self.get_mongo("useful_users")
        self.useful_mongo.create_index("id", unique=True)

        self._3000_10000_mongo = self.get_mongo("3000_10000")
        self._3000_10000_mongo.create_index("id", unique=True)

        self._100_3000_mongo = self.get_mongo("100_3000")
        self._100_3000_mongo.create_index("id", unique=True)

        self.less_100_mongo = self.get_mongo("0_100")
        self.less_100_mongo.create_index("id", unique=True)

        self.base_mongo = self.get_mongo("base_users")
        self.base_mongo.create_index("id", unique=True)

        self.sem = threading.BoundedSemaphore(100)
        self.standard_100 = 100
        self.standard_3000 = 3000
        self.standard_10000 = 10000
        #不要轻易开始初始化，会导致程序运行很久
        # self.chushihua()

    def get_mongo(self, collection_name):
        client = pymongo.MongoClient(config.MONGO_URL)
        mongodb = client['choujiang']
        collection = mongodb[collection_name]
        return collection

    def save_to_mongo(self, mongodb, user_id):
        try:
            mongodb.insert_one({
                "id": user_id,
                "tag": 0
            })
        except Exception as e:
            return

    def chushihua(self):
        useful_users = self.useful_mongo.find()
        less_100_users = self.less_100_mongo.find()
        _3000_10000_users = self._3000_10000_mongo.find()
        _100_3000_users = self._100_3000_mongo.find()
        for useful_user in useful_users:
            self.save_to_mongo(self.base_mongo, useful_user["id"])
        for no_use_user in less_100_users:
            self.save_to_mongo(self.base_mongo, no_use_user["id"])
        for no_use_user in _3000_10000_users:
            self.save_to_mongo(self.base_mongo, no_use_user["id"])
        for no_use_user in _100_3000_users:
            self.save_to_mongo(self.base_mongo, no_use_user["id"])

        # self.useful_mongo.delete_many({})
        # self.no_use_mongo.delete_many({})

    def parse_each_user(self, user):
        url = "https://weibo.com/u/%s" % user["id"]
        try:
            page = requests.post(tools.base_url, json={"url": url, "headers": self.headers})
        except Exception as e:
            print(e)
            self.sem.release()
            return

        page = json.loads(page.text)
        if page["type"] == "error":
            self.sem.release()
            return

        page = page["text"]
        follows_num_pattern = re.compile(r'(她|他|它)的粉丝\((\d+?)\)')
        try:
            # print(page)
            follows_num = follows_num_pattern.findall(page)[0][1]
            print(follows_num)
            if int(follows_num) < self.standard_100:
                self.save_to_mongo(self.less_100_mongo, user["id"])
            elif int(follows_num) < self.standard_3000:
                self.save_to_mongo(self._100_3000_mongo, user["id"])
            elif int(follows_num) < self.standard_10000:
                self.save_to_mongo(self._3000_10000_mongo, user["id"])
            else:
                self.save_to_mongo(self.useful_mongo, user["id"])
            self.base_mongo.delete_one({"id": user["id"]})
        except Exception as e:
            # print(e)
            pass
        self.sem.release()

    def parse_all_users(self, users, total):
        tsk = []
        number = 0
        for user in users:
            self.sem.acquire()
            print("total is %s, now is %s" % (total, number))
            number += 1
            t = threading.Thread(target=self.parse_each_user, args=(user,))
            t.start()
            tsk.append(t)
        for task in tsk:
            task.join()

    def seperate_users(self):
        try_times = 0
        while True:
            if try_times > 20:
                break
            try_times += 1
            total_users = self.base_mongo.find()
            total_users_count = self.base_mongo.count_documents({})
            if total_users_count < 1:
                break
            self.parse_all_users(total_users, total_users_count)


if __name__ == "__main__":
    Seperate_object = SeperateUsers()
    Seperate_object.seperate_users()
