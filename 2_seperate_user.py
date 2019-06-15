"""
把用户分为值得关注的和不值得关注的

每当来了新的一批账号，把新的账号存在base_users这个表中，然后先把当前的有用的和无用的账号和这批账号合并，把以前做的有用的和无用的账号的分类删除（因为数据可能比较旧了）
然后对这个合并之后的账号集合进行清洗

这个程序不用经常跑，一个月一次都是ok的
"""

import re
import requests
import pymongo
import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import tools
import threading
import json


class SeperateUsers(object):
    def __init__(self):
        # self.headers = {
        #     "Host": "weibo.com",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
        #     "Cookie": "SINAGLOBAL=1971032401731.4163.1551954096720; un=15110248779; SCF=AkxnN3UOg2_gI0lQpJs3Ce5OGPpjj6UqYzvn1zDxH3Uwl3b35CjAtVKOURGjNAkkh-iPd3fV3KdOrDRqiumv8x8.; SUHB=0wn1jo3H0zlFQX; webim_unReadCount=%7B%22time%22%3A1560429869784%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A2%2C%22msgbox%22%3A0%7D; SUB=_2AkMqXsoLdcPxrAZVm_0QzmLraotH-jyZi6P9An7uJhMyAxgv7nBXqSVutBF-XFJVO0gHZ69gfDqyu-jJLhcZggAo; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhQlbikHdp9PNYWkFUk2aa35JpVF02feK27eoBRS0M4; UOR=,,www.baidu.com; login_sid_t=08427fb0fafd381ee7671d7b96f4112e; cross_origin_proto=SSL; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; _s_tentry=www.baidu.com; wb_view_log=1920*10801; YF-V5-G0=27518b2dd3c605fe277ffc0b4f0575b3; Apache=4050300198651.866.1560477141158; ULV=1560477141176:3:3:3:4050300198651.866.1560477141158:1560432380350; WBtopGlobal_register_version=3cccf158e973a877; WBStorage=6b696629409558bc|undefined"
        # }
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            # "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "SINAGLOBAL=1971032401731.4163.1551954096720; un=15110248779; YF-V5-G0=44cd1a20bfa82176cbec01176361dd13; Ugrow-G0=9ec894e3c5cc0435786b4ee8ec8a55cc; login_sid_t=0b602882abb47dbd142e8c07ef97ec9e; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=5877733797022.269.1560558763856; ULV=1560558763863:1:1:1:5877733797022.269.1560558763856:; wb_view_log=1920*10801; SCF=AkxnN3UOg2_gI0lQpJs3Ce5OGPpjj6UqYzvn1zDxH3UwmLjFlPWfDk8nYDYifAlglTAHm8RER707cuzqjsbBd-0.; SUHB=0Jvg4uOsUahMEM; wb_view_log_5435529966=1920*10801; webim_unReadCount=%7B%22time%22%3A1560576572438%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhQlbikHdp9PNYWkFUk2aa35JpVF02feK27eoBRS0M4; SUB=_2AkMqWA0JdcPxrAZVm_0QzmLraotH-jyZjWT_An7uJhMyAxgv7lAmqSVutBF-XFtO3mZ2fNeexd3DEju6sYCRx46M; WBStorage=6b696629409558bc|undefined; UOR=,,login.sina.com.cn; YF-Page-G0=e57fcdc279d2f9295059776dec6d0214|1560576577|1560576571",
            "Host": "weibo.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
        }
        self.seperate_list = [0,100,200,400,600,1000,1500,2000,3000,4000,5000,6000,7000,8000,9000,10000,15000,20000,30000,50000,100000,200000,500000,1000000,1000000000]

        self.base_mongo = self.get_mongo("base_users")
        self.base_mongo.create_index("id", unique=True)
        for seperate_index in range(1,len(self.seperate_list)):
            start = self.seperate_list[seperate_index-1]
            end = self.seperate_list[seperate_index]
            mongo_db = self.get_mongo("%s_%s" % (start,end))
            mongo_db.create_index("id", unique=True)
        self.sem = threading.BoundedSemaphore(200)

        #不要轻易开始初始化，会导致程序运行很久
        # self.chushihua()

    def get_mongo(self, collection_name):
        #这是用来把g_weibo这个项目的用户id数据复制到抽奖机这个项目来
        # if collection_name == "base_users":
        #     client = pymongo.MongoClient(config.MONGO_URL)
        #     mongodb = client['weibo']
        #     users_id_collection = mongodb["users_id"]
        #     datas = users_id_collection.find()
        #     client = pymongo.MongoClient(config.MONGO_URL)
        #     mongodb = client['choujiang']
        #     base_collection = mongodb[collection_name]
        #     num = 0
        #     for data in datas:
        #         print(num)
        #         num  += 1
        #         base_collection.insert_one({"id":data["id"],"tag":0})
        #     return base_collection
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
        url = "https://weibo.com/u/%s?is_all=1" % user["id"]
        try:
            page = requests.post(tools.base_url, json={"url": url, "headers": self.headers})
        except Exception as e:
            print(e)
            self.sem.release()
            return

        page = json.loads(page.text)
        if page["type"] == "error":
            # print("aaa")
            # print(page["text"])
            self.sem.release()
            return

        page = page["text"]
        follows_num_pattern = re.compile(r'(她|他|它)的粉丝\((\d+?)\)')
        try:
            # print(page)
            follows_num = follows_num_pattern.findall(page)[0][1]
            print(follows_num)
            follows_num = int(follows_num)
            for end_index in range(len(self.seperate_list)):
                if follows_num < self.seperate_list[end_index]:
                    self.save_to_mongo(self.get_mongo("%s_%s" % (self.seperate_list[end_index-1],self.seperate_list[end_index])), user["id"])
                    break
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
            total_users = self.base_mongo.find({},no_cursor_timeout=True)
            total_users_count = self.base_mongo.count_documents({})
            if total_users_count < 1:
                break
            self.parse_all_users(total_users, total_users_count)


if __name__ == "__main__":
    Seperate_object = SeperateUsers()
    Seperate_object.seperate_users()
