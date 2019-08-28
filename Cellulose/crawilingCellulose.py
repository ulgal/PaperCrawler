#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
import os, sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

def hostedBySNU():
    # headless mode
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path="@geckodriver_path@")
    #
    # without headless
    # driver = webdriver.Firefox(executable_path="@geckodriver_path@")
    #
    # Login
    driver.get('https://lib.snu.ac.kr/user/login')
    # SNU Id
    driver.find_element_by_name('si_id').send_keys('@mySNU_ID@')
    # SNU Password
    driver.find_element_by_name('si_pwd').send_keys('@mySNU_password@')
    driver.find_element_by_xpath('//*[@id="snu-login-block-form"]/div//*[@id="edit-actions"]/input').click()
    time.sleep(5)
    # Find Link and get redirected page
    driver.get("https://ap01-a.alma.exlibrisgroup.com/view/action/uresolver.do?operation=resolveService&package_service_id=13703864020002591&institutionId=2591&customerId=2590")
    time.sleep(5)
    return driver

def getPaperListPage(year_cnt, month_cnt, paper_cnt, driver):
    try:
        if(paper_cnt<20):
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt))
        else:
            driver.get(journal_list_links + "/" + str(year_cnt) + "/" + str(month_cnt) + "/page/" + str(1 + int(paper_cnt/20)))
    except:
        driver.close()
        driver = hostedBySNU()
        return driver, False
    time.sleep(2)
    return driver, True

def getPaper(num, driver):
    try:
        driver.find_element_by_xpath('//div[contains(@class, "toc")]/ol/li[' + str(art_num) + ']/div/h3/a').click()
    except:
        driver.close()
        driver = hostedBySNU()
        return driver, None, False
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return driver, soup, True



# data container
keywordList = []
data = []
# Crawler Loop
journal_list_links = "http://lps3.link.springer.com.libproxy.snu.ac.kr/journal/10570"
for year_cnt in range(26, 0, -1):#94 to 19
    driver = hostedBySNU()
    for month_cnt in range(13, 0, -1):# Vol 1 ~ 12
        success = False
        while(not success):
            driver, success = getPaperListPage(year_cnt, month_cnt, 0, driver)
        paper_list_html = driver.page_source
        paper_list_soup = BeautifulSoup(paper_list_html, 'html.parser')
        paper_num = int(paper_list_soup.select('#kb-nav--main > div.toc > h2 > span')[0].text.strip()[1:3])
        for paper_cnt in range(0, paper_num): # get each paper
            success = False
            while(not success):
                driver, success = getPaperListPage(year_cnt, month_cnt, paper_cnt, driver)
            art_num = paper_cnt % 20 + 1
            success = False
            while(not success):
                driver, soup, success = getPaper(art_num, driver)
            # title, published year, keyword, abstract, etc..
            # fill below if need
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
                print(str(year_cnt-7) + " " + str(month_cnt) + " " + str(paper_cnt))
            for x in keyword:
                temp_data.append(x.text.strip())
                keywordList.append(x.text.strip())
            data.append(temp_data)
    # division
    keywordList.append(str(year_cnt-7) + " years end")
    driver.close()


# save file
df = pd.DataFrame(data)
r, c = df.shape
header = ["published", "Title"] + ["keyword" + str(x) for x in range(1, c-2)]
df.to_csv("cellulose_ALL.csv", index = False, encoding='utf-8-sig')

df_raw_keyWord = pd.DataFrame(keywordList)
df_raw_keyWord.to_csv("keyword_ALL_raw.csv", index = False,  encoding='utf-8-sig')


# Process Keyword
keywordList = pd.read_csv("keyword_ALL_raw.csv", index_col = None)
# check frequency
sorted_key, counted_key  = np.unique(keywordList, return_counts = True)
sorted_key = sorted_key.reshape(len(sorted_key), 1)
counted_key = counted_key.reshape(len(counted_key), 1)
keyWord = np.concatenate((sorted_key, counted_key), axis = 1)
df_keyWord = pd.DataFrame(keyWord)
df_keyWord.to_csv("keyword_ALL.csv", header = ["keyword", "frequency"], index = False, encoding='utf-8-sig')

