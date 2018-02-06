import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium
import bs4
import urllib.request as req
import re
import datetime
import time
import requests
import os
from konlpy import jvm
from konlpy.tag import Twitter
import timeit
import pandas as pd

text_file_name = ""
def get_url_list(input_date):
    eval_d = input_date

    user_agent = "'Mozilla/5.0"
    headers ={"User-Agent" : user_agent}

    page_url = "http://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId=000&date=" + str(eval_d)
    response = requests.get(page_url, headers=headers)
    html = response.text

    url_frags = re.findall('<a href="(.*?)"', html)
    url_list = []

    prev = ""
    for url_frag in url_frags:
        if prev == url_frag:
            continue
        elif "rankingSectionId=000" in url_frag:
            url_list.append("http://news.naver.com/" + url_frag)
            prev = url_frag

    return url_list

def gen_print_url(url_line):
    """
    주어진 기사 링크 URL로 부터 인쇄용 URL을 만들어 돌려준다.
    :param url_line:
    :return:
    """
    article_id = url_line[86:86+22]
    print_url = "http://news.naver.com/main/tool/print.nhn?" + article_id

    return print_url

def get_html(print_url) :
    """
    주어진 인쇄용 URL에 접근하여 HTML을 읽어서 돌려준다.
    :param print_url:
    :return:
    """
    user_agent = "'Mozilla/5.0"
    headers ={"User-Agent" : user_agent}

    response = requests.get(print_url, headers=headers)
    html = response.text

    return html

"""
def write_html(output_file, html):

    #주어진 HTML 텍스트를 출력 파일에 쓴다.
    #:param output_file:
    #:param html:
    #:return:


    output_file.write("{}\n".format(html))
"""

# html to text file

ARTICLE_DELIMITER = "@@@@@ ARTICLE DELMITER @@@@\n"
TITLE_START_PAT = '<h3 class="font1">'
TITLE_END_PAT = '</h3>'
DATE_TIME_START_PAT = u'기사입력 <span class="t11">'
BODY_START_PAT = '<div class="article_body">'
BODY_END_PAT = '<div class="article_footer">'
TIDYUP_START_PAT = '<div class="article_footer">'


def read_html_article(html_file):
    """
    HTML 파일에서 기사 하나를 읽어서 돌려준다.
    :param html_file:
    :return:
    """

    lines = []
    for line in html_file:
        if line.startswith(ARTICLE_DELIMITER):
            html_text = "".join(lines).strip()
            return html_text
        lines.append(line)

    return None

def strip_html(html_body):
    """
    HTML 본문에서 HTML 태그를 제거하고 돌려준다.
    :param html_body:
    :return:
    """
    page = bs4.BeautifulSoup(html_body, "html.parser")
    body = page.text

    return body

def tidyup(body):
    """
    본문에서 필요없는 부분을 자르고 돌려준다.
    :param body:
    :return:
    """

    p = body.find(TIDYUP_START_PAT)
    body = body[:p]
    body = body.strip()

    return body

def ext_body(html_text):
    """
    HTML 기사에서 본문을 추출하여 돌려준다.
    :param html_text:
    :return:
    """

    p = html_text.find(BODY_START_PAT)
    q = html_text.find(BODY_END_PAT)
    html_body = html_text[p + len(BODY_START_PAT):q]
    html_body = html_body.replace("<br />","\n")
    html_body = html_body.strip()
    body = strip_html(html_body)
    body = tidyup(body)

    return body



def empty_existing_file(filename):
    # existing_file = open(filename, "w", encoding="utf-8")
    # print("", file=existing_file)
    # existing_file.close()
    with open (filename + ".csv", "w", encoding="utf-8") as existing_file:
        pencil = csv.writer(existing_file)
        #pencil.writerow("")

def file_creation(filename):
    # existing_file = open(filename, "w", encoding="utf-8")
    # print("", file=existing_file)
    # existing_file.close()
    with open (filename + ".csv", "w", encoding="utf-8") as existing_file:
        pencil = csv.writer(existing_file)

def file_write(filename, text):
    # print("file write is called, text length : %d" % len(text))
    # translated_file = open(filename, "a", encoding="utf-8")
    # print(text, file=translated_file)
    # translated_file.close()
    with open (filename + ".csv", "a", encoding="utf-8" ) as translated_file:
        pencil = csv.writer(translated_file)
        pencil.writerow([text])


def add_to_urllist(url_list):
    with open("konlpy_url_list.csv", "a", encoding="utf-8") as url_list_file:
        pencil = csv.writer(url_list_file)
        for url in url_list:
            pencil.writerow([url])

def url_already_exist(url):
    try:
        with open("konlpy_url_list.csv", "r", encoding="utf-8") as url_list_file:
            file_reader = csv.reader(url_list_file)
            for line in file_reader:
                if url in line:
                    print("url in url_list file")
                    return True
    except FileNotFoundError :
        file_creation("konlpy_url_list")



if __name__ == "__main__":
    jvm.init_jvm()
    """
    네이버 뉴스기사를 수집한다.
    :return:
    """
    #driver = webdriver.Chrome()
    #driver = webdriver.Chrome('/Users/Celine/Documents/Projects/Picasso/chromedriver')
    driver = webdriver.PhantomJS('/Users/Celine/Documents/Projects/Picasso/phantomjs_macosx/bin/phantomjs')
    driver.get('http://papago.naver.com/')

    date = input('type in date : ')

    twitter = Twitter()
    #hannanum = Hannanum()

    # date
    while date > "20171101":
        start = timeit.default_timer()
        print("date : %s" % date)
        input_text = ""
        text_file_name = date
        count = 1
        urls = get_url_list(date)
        df = {}
        word_dic = {}
        # news article
        for url in urls:
            if url_already_exist(url) is True:
                continue
            count += 1
            print_url = gen_print_url(url)
            html = get_html(print_url)
            new_input = ext_body(html)
            #print("date : %s, count : %d" % (date, count))
            pos_list = twitter.pos(new_input)
            for word in pos_list: # for loop inside word count list
                if word[1] == "Noun" and len(word[0]) != 1:
                    if not (word[0] in word_dic):
                        word_dic[word[0]] = 0
                    word_dic[word[0]] += 1 # word count
        keys = sorted(word_dic.items(), key = lambda x:x[1], reverse=True)
        with open("wordcount_ko.csv", 'w', encoding="utf-8") as csvfile:
            pencil = csv.writer(csvfile, delimiter = ' ')
            for word, count in keys[:1000]:
            # pencil.writerow([date])
                pencil.writerow([keys[:1000]])

                print("{0}({1}) ".format(word,count), end="")
        print()


        stop = timeit.default_timer()
        print(stop - start)
        date = str(int(date) - 1)

    driver.quit()