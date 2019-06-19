"""
1. 本程序会给所有的被使用过的用户id打上这次的标签
2. 通过id和我给的时间戳来查找到所有的可能url
3.找出可能url中的有价值url，并打上标签
"""
import requests
import re
import pymongo
import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import time
import math
import tools
import json
import threading
import sys

PER_ID_NUM = 2000


class FindChoujiang(object):
    def __init__(self, standard_time, days):
        self.seperate_list = [0, 100, 200, 400, 600, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
                              15000, 20000, 30000, 50000, 100000, 200000, 500000, 1000000, 1000000000]
        self.TOTAL = 0
        self.lock = threading.Lock()
        self.useful_mongo = self.get_mongo("useful_ids")
        self.useful_mongo.create_index("id", unique=True)

        self.all_links_mongo = self.get_mongo("all_links_mongo")
        self.all_links_mongo.create_index("url", unique=True)

        self.useful_links_mongo = self.get_mongo("useful_links_mongo")
        self.useful_links_mongo.create_index("url", unique=True)

        self.sem = threading.BoundedSemaphore(100)
        timeArray = time.strptime(standard_time, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        self.tag = timeStamp * 1000
        self.end_tag = self.tag + 3600 * 24 * 1000 * int(days)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            # "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "SUB=_2AkMqXsoLdcPxrAZVm_0QzmLraotH-jyZi6P9An7uJhMyAxgv7nBXqSVutBF-XFJVO0gHZ69gfDqyu-jJLhcZggAo;",
            "Host": "weibo.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
        }
        print(self.tag)
        pass

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

    def find_and_save_useful_ids(self):

        # 这里是把我觉得有价值的id加进来
        total = 0
        for seperate_index in range(1, len(self.seperate_list)):
            start = self.seperate_list[seperate_index - 1]
            end = self.seperate_list[seperate_index]
            # 这里我是觉得粉丝数量少于5000的人是不会抽奖的
            if start < 5000:
                continue
            mongo_db = self.get_mongo("%s_%s" % (start, end))
            datas = mongo_db.find({"tag": 0}, no_cursor_timeout=True)
            for data in datas:
                print("find useful ids %s" % total)
                total += 1
                self.save_to_mongo(self.useful_mongo, data["id"])
                mongo_db.update_one({"id": data["id"]}, {"$set": {"tag": 1}})
        # 还应该有别的发现有价值id的方式，我以后再考虑
    def can_difficult(self,content):
        # 这个函数用来检测微博正文部分，看看这个微博是否有价值
        # print(content)
        if "\/\/" in content:
            content = content.split("\/\/")[0]

        content = content.strip()
        if content in "转发微博":
            return False

        if  "带话题" in content:
            return True

        # <i class=\"W_ficon ficon_cd_link\">O<\/i>抽奖详情<\/a>
        pattern_one = re.compile(r'<i class=\\"W_ficon ficon_cd_link\\">O<\\/i>抽奖详情<\\/a>')
        try:
                temp = pattern_one.findall(content)[0]
        except Exception as e:
                pass
        else:
                return True

        if "@微博抽奖平台" in content and ("恭喜" not in content) and ("祝贺" not in content):
            return True
        list_1 = ["转发","点赞",'评论']
        list_2 = ["抽","揪"]
        list_3 = ["送","赠"]
        for key_1 in list_1:
            if key_1 in content:
                for key_2 in list_2:
                    if key_2 in content:
                        for key_3 in list_3:
                            if key_3 in content:
                                return True
        return False
    def can_simple(self, content):
        # 这个函数用来检测微博正文部分，看看这个微博是否有价值
        # print(content)
        if "\/\/" in content:
            content = content.split("\/\/")[0]

        content = content.strip()
        if content in "转发微博":
            return False

        # print("*" * 100)
        # print(content)
        # print("Y" * 100)
        zaoyin_cihui = ["发送", "要送", "推送", "接送", "送机", "发现", "发改委", "发行", "发展",
                        "发布", "沙发", "引发", "发现", "发烧", "发出", "无关", "发给", "头发", "植发",
                        "发展","发明",
                        "评判",
                        "幸福", "祝福",
                        "利用",
                        "书评", "评价", "好评", "差评",
                        "关爱", "关心", "关于", "相关", "机关", "关照", "无关", "关系", "关怀", "关切",
                        "关门", "关闭", "海关","关键","关联",
                        "抽查",
                        "赞扬", "赞颂",
                        "赠与", "赠予",
                        "中转", "转机", "转变", "转换","一转"
                        ]
        for zaoyin in zaoyin_cihui:
            content = content.replace(zaoyin, "")
        # 根据下面这些条件来选出抽奖信息
        # with_song = ["福", "利", "奖", '抽']
        # if "送" in content:
        #     for key in with_song:
        #         if key in content:
        #             return True
        # if "赠" in content:
        #     return True
        if "带话题" in content:
            return True
        # <i class=\"W_ficon ficon_cd_link\">O<\/i>抽奖详情<\/a>
        pattern_one = re.compile(r'<i class=\\"W_ficon ficon_cd_link\\">O<\\/i>抽奖详情<\\/a>')
        try:
            temp = pattern_one.findall(content)[0]
        except Exception as e:
            pass
        else:
            return True

        if "@微博抽奖平台" in content and ("恭喜" not in content) and ("祝贺" not in content):
            return True

        key_list_1 = ["转", "关", "赞", "评"]
        key_list_2 = ["发", "抽", "奖", "送", "赠", '揪', '给']
        key_list_3 = ["抽", "奖", "送", "赠", '揪', "关", "赞", "评", "给"]
        for key_1 in key_list_1:
            if key_1 in content:
                for key_2 in key_list_2:
                    if key_2 in content:
                        for key_3 in key_list_3:
                            if key_3 in content:
                                return True

        return False

        pass

    def parse_each_urls(self, url_block):
        url = url_block["url"]
        # url = "https://weibo.com/2261524662/HyGRR9U33?from=page_1005052261524662_profile&wvr=6&mod=weibotime&type=comment"
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

        content_pattern = re.compile(r'<div class=\\"WB_text W_f14\\"([\s\S]+?)>\\n([\s\S]+?)<\\/div>')
        content = content_pattern.findall(page)
        try:
            content = content[0][1]
        except Exception as e:
            print(e)
            self.sem.release()
            return
        # if self.can_simple(content):
        #     try:
        #         self.useful_links_mongo.insert_one({"url": url_block["url"], "tag": 0})
        #     except Exception as e:
        #         pass
        if self.can_difficult(content):
            try:
                self.useful_links_mongo.insert_one({"url": url_block["url"], "tag": 0})
            except Exception as e:
                pass

        self.all_links_mongo.update_one({"_id": url_block["_id"]}, {"$set": {"tag": 1}})
        self.sem.release()

    def parse_all_urls(self):
        try_times = 0
        while True:
            if try_times > 1:
                break
            try_times += 1
            all_urls = self.all_links_mongo.find({"tag": 0})
            all_urls_count = self.all_links_mongo.count_documents({"tag": 0})
            if all_urls_count < 10:
                break
            tsk = []
            now_number = 0
            for url in all_urls:
                print("total is %s ,now is %s" % (all_urls_count, now_number))
                now_number += 1
                self.sem.acquire()
                t = threading.Thread(target=self.parse_each_urls, args=(url,))
                t.setDaemon(True)
                t.start()
                tsk.append(t)
            time.sleep(10)
            # for task in tsk:
            #     print(len(threading.enumerate()))
            #     task.join()
            #     task.stop()
            print("----")

    # 这个函数获得有价值用户的所有新发的微博url
    def parse_each_useful_id(self, user):
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
        try:
            # page_id_pattern = re.compile(r"CONFIG['page_id']='([\d+?])'")
            # page_id = page_id_pattern.findall(page)[0]
            # 'href=\"\/5918660052\/HlE7QpDoy?from=page_1006065918660052_profile&wvr=6&mod=weibotime\" title=\"2019-03-19 16:21\" date=\"1552983688000\" class=\"S_txt2\" node-type=\"feed_list_item_date\" suda-data='
            links_pattern = re.compile(
                r'\\\/(\d+?)\\\/([\d\w]+?)\?from=page_(\d+?)_profile&wvr=6&mod=weibotime([\s\S]+?)date=\\"(\d+)')
            all_links = links_pattern.findall(page)

            for link in all_links:
                if str(link[0]) in str(link[2]) and int(link[4]) >= self.tag and int(link[4]) < self.end_tag:
                    url_link = "https://weibo.com/%s/%s?from=page_%s_profile&wvr=6&mod=weibotime&type=comment" % (
                        link[0], link[1], link[2])
                    self.all_links_mongo.insert_one({"url": url_link, "tag": 0})
        except Exception as e:
            self.sem.release()
            return
        print(user["id"])
        self.useful_mongo.update_one({"id": user["id"]}, {"$set": {"tag": self.tag}})
        self.lock.acquire()
        self.TOTAL += 1
        self.lock.release()
        self.sem.release()

    def parse_all_useful_ids(self):
        try_times = 0
        while True:
            useful_ids = self.useful_mongo.find({"tag": {"$ne": self.tag}}, no_cursor_timeout=True)
            useful_ids_count = self.useful_mongo.count_documents({"tag": {"$ne": self.tag}})
            if useful_ids_count < 1:
                break
            if try_times > 1:
                break
            try_times += 1
            tsk = []
            now_number = 0
            for useful_id in useful_ids:
                if self.TOTAL > PER_ID_NUM:
                    break
                print("total is %s, now is %s" % (useful_ids_count, now_number))
                now_number += 1
                self.sem.acquire()
                t = threading.Thread(target=self.parse_each_useful_id, args=(useful_id,))
                t.setDaemon(True)
                t.start()
                tsk.append(t)
            # print("aaa")
            # for task in tsk:
            #     print("bbb")
            #     print(len(threading.enumerate()))
            #     task.join()
            #     print("ccc")
            time.sleep(20)
            if self.TOTAL > PER_ID_NUM:
                self.lock.acquire()
                self.TOTAL = 0
                self.lock.release()
                break
        pass

    def total_parse(self):
        try_times = 0
        useful_ids_count = self.useful_mongo.count_documents({"tag": {"$ne": self.tag}})
        while useful_ids_count > PER_ID_NUM and try_times < 100:
            try_times += 1
            self.parse_all_useful_ids()
            self.parse_all_urls()


if __name__ == "__main__":
    try:
        riqi = sys.argv[1]
    except:
        riqi = "2019-06-15"
    try:
        shijian = sys.argv[2]
    except:
        shijian = "00:00:00"
    try:
        days = sys.argv[3]
    except:
        days = "1"
    FindObject = FindChoujiang("%s %s" % (riqi, shijian), days)
    # FindObject = FindChoujiang("2019-06-10 00:00:00")
    FindObject.find_and_save_useful_ids()
    # FindObject.parse_all_useful_ids()
    FindObject.total_parse()
