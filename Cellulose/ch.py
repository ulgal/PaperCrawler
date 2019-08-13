#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os, sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup


# In[3]:


def hostedBySNU():
    path = "./firefoxdriver.exe"
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path="@firefox driver path@")
    # Login
    driver.get('https://lib.snu.ac.kr/user/login')
    # SNU Id
    driver.find_element_by_name('si_id').send_keys('@userID@')
    # SNU Password
    driver.find_element_by_name('si_pwd').send_keys('@userPASSWORD@')
    driver.find_element_by_xpath('//*[@id="snu-login-block-form"]/div//*[@id="edit-actions"]/input').click()
    time.sleep(2)
    # Find Link and get redirected page, get from html
    driver.get("@hosting URL@")
    time.sleep(2)
    return driver


# In[4]:


def getArticleListPage(year_cnt, month_cnt, article_cnt, driver):
    try:
        if(article_cnt<20):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt))
        elif(article_cnt >= 20 and article_cnt < 40):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/2")
        elif(article_cnt >= 40 and article_cnt < 60):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/3")
        elif(article_cnt >= 60 and article_cnt < 80):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/4")
        elif(article_cnt >= 80 and article_cnt < 100):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/5")
        elif(article_cnt >= 10 and article_cnt < 120):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/6")
    except TimeoutException as ex:
        driver.close()
        driver = hostedBySNU()
        return driver, False
    except NoSuchElementException as ex2:
        driver.close()
        driver = hostedBySNU()
        return driver, False
    time.sleep(1.5)
    return driver, True


# In[5]:


def getArticle(num, driver):
    try:
        driver.find_element_by_xpath('//div[contains(@class, "toc")]/ol/li[' + str(art_num) + ']/div/h3/a').click()
    except TimeoutException as ex:
        driver.close()
        driver = hostedBySNU()
        return driver, None, False
    except NoSuchElementException as ex2:
        driver.close()
        driver = hostedBySNU()
        return driver, None, False
    except:
        driver.close()
        driver = hostedBySNU()
        return driver, None, False
    time.sleep(1.5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return driver, soup, True


# In[7]:


# Crawler Loop
journal_list_links = "http://lps3.link.springer.com.libproxy.snu.ac.kr/journal/10570"
for year_cnt in range(26, 0, -1):
    driver = hostedBySNU()
    time.sleep(1.5)
    for month_cnt in range(13, 0, -1):
        success = False
        while(not success):
            driver, success = getArticleListPage(year_cnt, month_cnt, 0, driver)
        article_list_html = driver.page_source
        article_list_soup = BeautifulSoup(article_list_html, 'html.parser')
        article_num = int(article_list_soup.select('#kb-nav--main > div.toc > h2 > span')[0].text.strip()[1:3])
        for article_cnt in range(0, article_num):
            success = False
            while(not success):
                driver, success = getArticleListPage(year_cnt, month_cnt, article_cnt, driver)
            art_num = article_cnt % 20 + 1
            success = False
            while(not success):
                driver, soup, success = getArticle(art_num, driver)
            temp_data = []
            pub_year = soup.select('p.icon--meta-keyline')
            title = soup.select('h1.ArticleTitle')
            keyword = soup.select('div.KeywordGroup > span')
            for x in pub_year:
                pub_year_str = x.text.strip()
                cnt = 0
                for y in pub_year_str:
                    if(y==','):
                        break
                    cnt+=1
                temp_data.append(pub_year_str[:cnt])
            for x in title:
                temp_data.append(x.text.strip())
                print(str(year_cnt-7) + " " + str(month_cnt) + " " + str(article_cnt))
            for x in keyword:
                temp_data.append(x.text.strip())
                keywordList.append(x.text.strip())
            data.append(temp_data)
    keywordList.append(str(year_cnt-7) + "years end")
    driver.close()


# In[59]:


sorted_key, counted_key  = np.unique(keywordList, return_counts = True)
sorted_key = sorted_key.reshape(len(sorted_key), 1)
counted_key = counted_key.reshape(len(counted_key), 1)
keyWord = np.concatenate((sorted_key, counted_key), axis = 1)
df_keyWord = pd.DataFrame(keyWord)
df_keyWord.to_csv("keyword_ALL.csv", header = ["keyword", "frequency"], index = False, encoding='utf-8-sig')

df = pd.DataFrame(data)
r, c = df.shape
df.to_csv("cellulose_ALL.csv", index = False, encoding='utf-8-sig')

df_raw_keyWord = pd.DataFrame(keywordList)
df_raw_keyWord.to_csv("keyword_ALL_raw.csv", index = False,  encoding='utf-8-sig')


# In[ ]:


driver.close()

