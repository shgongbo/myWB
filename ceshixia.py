import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    # "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    # "Connection": "keep-alive",
    "Cookie": "SINAGLOBAL=1971032401731.4163.1551954096720; un=15110248779; SCF=AkxnN3UOg2_gI0lQpJs3Ce5OGPpjj6UqYzvn1zDxH3Uwl3b35CjAtVKOURGjNAkkh-iPd3fV3KdOrDRqiumv8x8.; SUHB=0wn1jo3H0zlFQX; webim_unReadCount=%7B%22time%22%3A1560429869784%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A2%2C%22msgbox%22%3A0%7D; SUB=_2AkMqXsoLdcPxrAZVm_0QzmLraotH-jyZi6P9An7uJhMyAxgv7nBXqSVutBF-XFJVO0gHZ69gfDqyu-jJLhcZggAo; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhQlbikHdp9PNYWkFUk2aa35JpVF02feK27eoBRS0M4; UOR=,,www.baidu.com; login_sid_t=08427fb0fafd381ee7671d7b96f4112e; cross_origin_proto=SSL; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; _s_tentry=www.baidu.com; wb_view_log=1920*10801; YF-V5-G0=27518b2dd3c605fe277ffc0b4f0575b3; Apache=4050300198651.866.1560477141158; ULV=1560477141176:3:3:3:4050300198651.866.1560477141158:1560432380350; WBtopGlobal_register_version=3cccf158e973a877; WBStorage=6b696629409558bc|undefined; YF-Page-G0=aac25801fada32565f5c5e59c7bd227b|1560483132|1560483022",
    # "Cookie":"",
    "Host": "weibo.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
}
page = requests.get("https://weibo.com/u/3297975461?is_all=1", headers = headers, allow_redirects=False)
# page = requests.get("https://weibo.com/608914561", headers = headers, allow_redirects=False)
print(page)
print(page.content)
print(page.headers)
print(page.history)
print(page.ok)
print(page.text)
