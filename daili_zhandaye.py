import redis
import socket
import requests
import time
import random
if socket.gethostname() =="ISZ4DI1Z6MV6Z6K":
    print("aaa")
    import config
else:
    print("bbb")
    import product_config as config

class zhandaye_ip(object):
    def __init__(self):
        self.get_proxy_url = "http://www.zdopen.com/ShortProxy/GetIP/?api=201903251023417353&akey=df50159e29464e0d&order=2&type=1"
        self.set_ip_url = "http://www.zdopen.com/ShortProxy/BindIP/?api=%s&akey=df50159e29464e0d&i=%s" % (
            config.ZHANDAYE_API_ID, 2)
        self.redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    def get_proxy(self):
        print("222")
        total = 0
        while True:

            try:
                data = requests.get(self.get_proxy_url).text
                print("*"* 100)
                print(data)
                print("&" * 100)
                if "bad" in data:
                    print(data)
                    time.sleep(1)
                    # total += 1
                    # if total > 10:
                    #     requests.get(self.set_ip_url)
                    #     total = - 50
                    continue
                # print(data)
                for proxy_ip in data.split("\n"):
                    print("bbb")
                    self.redis.set("%.6f".replace(".", "") % time.process_time() + str(random.randint(0, 10000)),
                                   proxy_ip, ex=170)
                # total = 0
                # for proxy_ip in data.split("\n"):
                #     total += 1
                #     self.redis.set(total,
                #                    proxy_ip, ex=10)
            except Exception as e:
                print(e)
                total = 0
                requests.get(self.set_ip_url)
            finally:
                total = 0
                # requests.get(self.set_ip_url)
                time.sleep(29)

while True:
    try:
        z = zhandaye_ip()
        z.get_proxy()
    except Exception as e:
        print(e)
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        continue
