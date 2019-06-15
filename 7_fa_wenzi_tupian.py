from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import os
from selenium.webdriver.common.by import By
import time
import random
import sys
#basicSettings,这些设置都很重要
shoujihao = "15110248779"
mima = "gongbo0801"
uid = "5435529966"
WENZI_TOTAL_NUM = 20
PIC_TOTAL_NUM = 20
WENZI_PATH = "wenzi_and_tupian/wenzi.txt"

PIC_PATH = sys.path[0] +"\wenzi_and_tupian\%s.jpg"
# WENZI_NUM = random.randint(1, 5)
# TUPIAN_NUM = random.random(1, 5)

WENZI_NUM = 3
TUPIAN_NUM = 2

while True:
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get('https://weibo.com/login.php')
    browser.maximize_window()
    WebDriverWait(browser, 100, 0.1).until(lambda x: x.find_element_by_id("loginname"))
    name = browser.find_element_by_id("loginname")
    name.send_keys(shoujihao)
    time.sleep(1)
    password = browser.find_element_by_name("password")
    password.send_keys(mima)
    time.sleep(1)
    login_button = browser.find_element_by_class_name("W_btn_a.btn_32px ")
    login_button.click()
    try:
        WebDriverWait(browser, 30, 0.1).until(EC.presence_of_element_located((By.CLASS_NAME, "nameBox")))
    except Exception as e:
        browser.quit()
        continue
    else:
        break



def get_wenzi():
    with open(WENZI_PATH, "r") as file:
        random_wenzi_index = random.randint(0, WENZI_TOTAL_NUM)
        return file.readlines()[random_wenzi_index]


def get_tupian():
    pic_list = []
    pic_num = random.randint(1, 9)
    for i in range(pic_num):
        pic_index = random.randint(0, PIC_TOTAL_NUM)
        pic_path = PIC_PATH % pic_index
        pic_list.append(pic_path)

    return pic_list


browser.get('https://weibo.com/u/%s?from=feed&loc=nickname&is_all=1' % uid)
"S_txt1 t_link"
WebDriverWait(browser, 10, 0.1).until(EC.presence_of_element_located((By.CLASS_NAME, "W_ficon.ficon_send.S_ficon")))

# print("aa")
# if "我的收藏" in browser.page_source:
#     print("登录成功！")
#     break
# else:
#     print("登录失败！")
#     browser.refresh()
#     WebDriverWait(browser, 10, 0.1).until(EC.presence_of_element_located((By.ID,"loginname")))

for i in range(WENZI_NUM):
    while True:
        try:
            browser.find_element_by_class_name("W_ficon.ficon_send.S_ficon").click()
            print("try once")
            WebDriverWait(browser, 5, 0.1).until(EC.presence_of_element_located((By.CLASS_NAME, "W_layer_title")))
        except:
            continue
        else:
            break
    input_textarea = browser.find_element_by_xpath('//textarea[starts-with(@class,"W_input")]')
    input_textarea.send_keys(get_wenzi())
    time.sleep(1)
    browser.find_element_by_class_name("W_btn_a.btn_30px ").click()
    time.sleep(30)

for i in range(TUPIAN_NUM):
    while True:
        try:
            browser.find_element_by_class_name("W_ficon.ficon_send.S_ficon").click()
            print("try once")
            WebDriverWait(browser, 5, 0.1).until(EC.presence_of_element_located((By.CLASS_NAME, "W_layer_title")))
        except:
            continue
        else:
            break
    # picture_button = browser.find_element_by_xpath('//*[@id="swf_upbtn_156056956360033"]')
    input_textarea = browser.find_element_by_xpath('//textarea[starts-with(@class,"W_input")]')
    input_textarea.send_keys(get_wenzi())
    while True:
        try:
            browser.find_element_by_class_name("W_ficon.ficon_image").click()
            time.sleep(1)
            picture_button = browser.find_element_by_xpath('//input[starts-with(@id,"swf_upbtn_")]')
        except:
            continue
        else:
            break
    pic_list = get_tupian()
    for i in range(len(pic_list)):
        picture_button.send_keys(pic_list[i])
    # //*[@id="layer_15605759690581"]/div[2]/div[3]/div/div/div/div[2]/textarea
    # input_textarea = browser.find_element_by_class_name("input")

    time.sleep(5 * len(pic_list))
    browser.find_element_by_class_name("W_btn_a.btn_30px ").click()

browser.quit()

