#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


# In[2]:


# execute chromedriver
path = "./chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("--dns-prefetch-disable")
driver = webdriver.Chrome(path, chrome_options=options)
#driver = webdriver.Chrome(path)


# In[3]:


# Login
driver.get('https://lib.snu.ac.kr/user/login')
# SNU Id
driver.find_element_by_name('si_id').send_keys('@@SNUID@@')
# SNU Password
driver.find_element_by_name('si_pwd').send_keys('@@SNUPASSWORD@@')
driver.find_element_by_xpath('//*[@id="snu-login-block-form"]/div//*[@id="edit-actions"]').click()


# In[4]:


# Search Journal
driver.get('https://lib.snu.ac.kr')
elem = driver.find_element_by_id("edit-search")
elem.clear()
# Journal Name
elem.send_keys("Cellulose")
elem.submit()


# In[5]:


# Cellulose Journal permailink
driver.get("https://primoapac01.hosted.exlibrisgroup.com/permalink/f/1l6eo7m/82SNU_INST51488292290002591")


# In[6]:


# Find Link and get redirected page, get from html
driver.get("https://ap01-a.alma.exlibrisgroup.com/view/action/uresolver.do?operation=resolveService&package_service_id=13703864020002591&institutionId=2591&customerId=2590")


# In[7]:


# for save the data
data = []
keywordList = []


# In[8]:


# for check data num
article_cnt_for_check = 1


# In[ ]:


# Crawler Loop
journal_list_links = "http://lps3.link.springer.com.libproxy.snu.ac.kr/journal/10570";
for year_cnt in range(26, 0, -1):
    for month_cnt in range(1, 13):
        driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt))
        article_list_html = driver.page_source
        article_list_soup = BeautifulSoup(article_list_html, 'html.parser')
        article_num = int(article_list_soup.select('#kb-nav--main > div.toc > h2 > span')[0].text.strip()[1:3])
        for article_cnt in range(1, article_num):
            #driver.implicitly_wait(1)
            if(article_cnt<20):
                driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt))
            if(article_cnt >= 20 and article_cnt < 40):
                driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/2")
            if(article_cnt >= 40 and article_cnt < 60):
                driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/3")
            if(article_cnt >= 60 and article_cnt < 80):
                driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/4")
            art_num = article_cnt % 20 + 1
            try:
               driver.find_element_by_xpath('//div[contains(@class, "toc")]/ol/li[' + str(art_num) + ']/div/h3/a').click()
            except TimeoutException as ex:
               print(ex.Message)
               driver.navigate().refresh()
            #driver.implicitly_wait(1)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
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
                print(str(article_cnt_for_check) + " " + x.text.strip())
                article_cnt_for_check += 1
            for x in keyword:
                temp_data.append(x.text.strip())
                keywordList.append(x.text.strip())
            data.append(temp_data)


# In[ ]:





# In[ ]:


df = pd.DataFrame(data)


# In[ ]:


df.to_csv("cellulose.csv", index = False, encoding='utf-8-sig')




# In[ ]:


keywordSet = Set(keywordList)


# In[14]:


r, c = df.shape
df.to_csv("cellulose.csv", header = ["Publish", "Title", "Keyword","Keyword","Keyword","Keyword","Keyword" "Keyword","Keyword","Keyword","Keyword","Keyword","Keyword","Keyword" ], index = False, encoding='utf-8-sig')


# In[ ]:





# In[ ]:


driver.close()

