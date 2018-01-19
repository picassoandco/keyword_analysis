import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium
import bs4
import urllib.request as req
import re
import datetime
from time import sleep
import time
import requests
import os.path
from collections import Counter
import nltk

text_file_name = ""

def get_url_list(input_date, section_id):
    eval_d = input_date

    user_agent = "'Mozilla/5.0"
    headers ={"User-Agent" : user_agent}

    page_url = "http://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId=" + section_id + "&date=" + str(eval_d)
    response = requests.get(page_url, headers=headers)
    html = response.text

    url_frags = re.findall('<a href="(.*?)"', html)
    url_list = []

    prev = ""
    for url_frag in url_frags:
        if prev == url_frag:
            continue
        elif "type=1&rankingSectionId=" in url_frag:
            url_list.append("http://news.naver.com/" + url_frag)
            prev = url_frag
    print(url_list)
    non = input("would you stop?")

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

# html to text file

ARTICLE_DELIMITER = "@@@@@ ARTICLE DELMITER @@@@\n"
TITLE_START_PAT = '<h3 class="font1">'
TITLE_END_PAT = '</h3>'
DATE_TIME_START_PAT = u'기사입력 <span class="t11">'
BODY_START_PAT = '<div class="article_body">'
BODY_END_PAT = '<div class="article_footer">'
TIDYUP_START_PAT = '<div class="article_footer">'

def create_text_file(text_file_name):
    """
    텍스트 기사 파일을 만들어 파일 객체를 돌려준다.
    :param text_file_name:
    :return:
    """

    text_file = open(text_file_name, "w", encoding="utf-8")

    return text_file

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

"""
def ext_title(html_text):

    #HTML 기사에서 제목을 추출하여 돌려준다.
    #:param html_text:
    #:return:
    #
    p = html_text.find(TITLE_START_PAT)
    q = html_text.find(TITLE_END_PAT)
    title = html_text[p + len(TITLE_START_PAT):q]
    title = title.strip()

    return title
"""

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

def auto_translate(input_text, driver, section_id):
    try:
        driver.find_element_by_id('txtSource').send_keys(input_text)
    except selenium.common.exceptions.UnexpectedAlertPresentException:
        print("you have exceeded the maximum number of characters")
        click_translate(driver)
    click_translate(driver)
    translated_text = driver.find_element_by_id('txtTarget').text
    file_write(text_file_name, translated_text, section_id)
    driver.refresh()

def click_translate(driver):
    try:
        driver.find_element_by_id("btnTranslate").click()
        while not driver.find_element_by_id('txtTarget').text:
            sleep(1)
    except selenium.common.exceptions.NoSuchElementException:
        sleep(3)
        print("network connection is not stable")
        click_translate(driver)

def file_creation(filename, section_id):
    # existing_file = open(filename, "w", encoding="utf-8")
    # print("", file=existing_file)
    # existing_file.close()
    directory = get_directory_name(section_id)
    with open (directory + "/" + filename + ".csv", "w", encoding="utf-8") as existing_file:
        pencil = csv.writer(existing_file)
        #pencil.writerow("")

def file_write(filename, text, section_id):
    # print("file write is called, text length : %d" % len(text))
    # translated_file = open(filename, "a", encoding="utf-8")
    # print(text, file=translated_file)
    # translated_file.close()
    directory = get_directory_name(section_id)
    if not os.path.isfile(directory + "/" + filename + ".csv"):
        file_creation(filename, section_id)
    with open (directory + "/" + filename + ".csv", "a", encoding="utf-8" ) as translated_file:
        pencil = csv.writer(translated_file)
        pencil.writerow([text])

def long_article_handler(old, new, driver, section_id):
    auto_translate(old, driver, section_id)
    iteration = len(new) // 5000
    print("length = %d, iteration = %d" % (len(new), iteration))
    for i in range(0, iteration):
        start = i * 5000
        end = (i+1) * 5000 - 1
        print("i : %d, start = %d, end = %d" % (i, start, end))
        auto_translate(new[start:end], driver, section_id)

    return new[end:]

def get_directory_name(section_id):
    if section_id == "100":
        return "politics"
    elif section_id == "101":
        return "economics"
    elif section_id == "102":
        return "society"
    elif section_id == "103":
        return "culture"
    elif section_id == "104":
        return "oversea"
    elif section_id == "105":
        return "technology"

def add_to_urllist(url_list):
    with open("url_list.csv", "a", encoding="utf-8") as url_list_file:
        pencil = csv.writer(url_list_file)
        for url in url_list:
            pencil.writerow([url])

def url_already_exist(url):
    with open("url_list.csv", "r", encoding="utf-8") as url_list_file:
        file_reader = csv.reader(url_list_file)
        for line in file_reader:
            if url in line:
                print("url in url_list file")
                return True

def word_count_en(filename):
    doc_en = open(filename, 'r')
    total = []
    while True:
        line = doc_en.readline()
        texts = nltk.word_tokenize(line)
        if not line:
            break
        total += texts
    nonPunct = re.compile('.*[A-Za-z0-9].*')
    filtered = [w for w in total if nonPunct.match(w)]
    counts = Counter(filtered)
    print(counts)
    doc_en.close()



if __name__ == "__main__":
    """
    네이버 뉴스기사를 수집한다.
    :return:
    """
    #driver = webdriver.Chrome()
    driver = webdriver.Chrome('/Users/Celine/Documents/Projects/Picasso/chromedriver')
    #driver = webdriver.PhantomJS('/Users/Celine/Documents/Projects/Picasso/phantomjs_macosx/bin/phantomjs')
    driver.get('http://papago.naver.com/')

    date = input('type in date : ')

    while True:
        print("date : %s" % date)
        input_text = ""
        text_file_name = date

        for section in range(100, 106):
            urls = get_url_list(date, str(section))
            count = 1
            url_bundle = []
            for url in urls:
                if url_already_exist(url) is True:
                    continue
                url_bundle.append(url)
                print("ID : %s, count : %d" %(get_directory_name(str(section)), count))
                count += 1
                print_url = gen_print_url(url)
                html = get_html(print_url)
                new_input = ext_body(html)
                if len(new_input) >= 5000:
                    input_text = long_article_handler(input_text, new_input, driver, str(section))
                    add_to_urllist(url_bundle)
                    print(len(url_bundle))
                    url_bundle = []
                elif len(input_text) + len(new_input) >= 5000:
                    auto_translate(input_text, driver, str(section))
                    add_to_urllist(url_bundle)
                    print(len(url_bundle))
                    input_text = new_input
                    url_bundle = []
                else:
                    input_text += new_input
            auto_translate(input_text, driver, str(section))
            add_to_urllist(url_bundle)
            print("len(url_bundle) : "%len(url_bundle))
            url_bundle = []

        date = int(date) - 1
        date = str(date)

    driver.quit()

