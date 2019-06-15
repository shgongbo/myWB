from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
import  selenium.webdriver.support.expected_conditions as EC
import os
from selenium.webdriver.common.by import By
import time
shoujihao = "15110248779"
mima = "gongbo0801"
# browser = webdriver.Chrome(ChromeDriverManager().install())
# browser.get('https://weibo.com/login.php')
# browser.maximize_window()
# WebDriverWait(browser, 100, 0.1).until(lambda  x:x.find_element_by_id("loginname"))
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


# js = 'window.open("https://weibo.com/5408745659/HyjbnEaHd?from=page_1005055408745659_profile&wvr=6&mod=weibotime&type=comment");'
# browser.execute_script(js)
# browser.get("https://weibo.com/5408745659/HyjbnEaHd?from=page_1005055408745659_profile&wvr=6&mod=weibotime&type=comment")
if os.path.exists("used.txt"):
    with open("used.txt","r") as file2:
        all_used_links = file2.readlines()
else:
    all_used_links = []
with open("used.txt","a") as file2:
    with open("useful_links.txt","r") as file:
        useful_links = file.readlines()
        # first_useful_link = useful_links[0]
        # browser.get(first_useful_link)
        for useful_link  in useful_links:
            if useful_link in all_used_links:
                continue
            js = 'window.open("%s");' % useful_link.strip("\n")
            browser.execute_script(js)
            while True:
                if len(browser.window_handles) < 2:
                    break
                time.sleep(0.1)
            file2.write(useful_link)


