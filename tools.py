import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config
import redis
proxy_redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

def get_proxy():
        proxy = proxy_redis.get(proxy_redis.randomkey())
        ip = str(proxy)
        ip = ip[2:]
        ip = ip.replace(r"\r", "")
        ip = ip.replace(r"\\", "")
        ip = ip.replace("'", "")
        return {"http": ip, "https": ip}
headers = {
            "Host": "weibo.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
            # "Cookie": config.COOKIE(),
            # "Cookie":"SINAGLOBAL=1971032401731.4163.1551954096720; httpsupgrade_ab=SSL; _s_tentry=passport.weibo.com; Apache=1115440246836.5298.1555483935581; ULV=1555483935623:1:1:1:1115440246836.5298.1555483935581:; login_sid_t=4abae5dba09e7acb31db46477dfc5bd2; cross_origin_proto=SSL; Ugrow-G0=7e0e6b57abe2c2f76f677abd9a9ed65d; WBStorage=201904221506|undefined; YF-V5-G0=694581d81c495bd4b6d62b3ba4f9f1c8; wb_view_log=1920*10801; WBtopGlobal_register_version=2019042215; SCF=AkxnN3UOg2_gI0lQpJs3Ce5OGPpjj6UqYzvn1zDxH3Uw43uiu_lmr4IG_4FY0bjHgkG1-j8obsIOCEZ5UiUwou8.; SUB=_2A25xuRhwDeRhGeFO61EV9izOzDqIHXVSzw64rDV8PUNbmtBeLU3GkW9NQYeTUpWskDZ0pQdJe4XqhSzslBiRyPZ9; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5z_53I4r6up8LNCpJUK4ob5JpX5K2hUgL.FoM7eheXSozES0q2dJLoIX2LxK.L1-zL1h-LxKqL1h5L1-xVMgHj9gp71KMfeEH8SE-4BC-RSEH8SE-4SFHWBbH8Sb-ReE-4BEH8SC-RSFHFxntt; SUHB=0N21NQfux1ylZw; ALF=1556521630; SSOLoginState=1555916832; un=17660433710; wvr=6; YF-Page-G0=140ad66ad7317901fc818d7fd7743564|1555916835|1555916835; wb_view_log_7003462276=1920*10801; webim_unReadCount=%7B%22time%22%3A1555916836277%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A35%2C%22msgbox%22%3A0%7D"

}

base_url = config.url