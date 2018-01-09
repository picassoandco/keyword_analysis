
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import bs4
import urllib.request as req
import re
import datetime
from time import sleep
import time
import requests
import os

text_file_name = "news"

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
def pause():
    """
    3초동안 쉰다.
    :return:
    """
    time.sleep(3)

def close_file(file):
    """
    출력 파일을 닫는다.
    :param output_file:
    :return:
    """

    file.close()

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

def auto_translate(input_text, driver):
    driver.find_element_by_id('txtSource').send_keys(input_text)
    sleep(1)
    driver.find_element_by_id("btnTranslate").click()
    while not driver.find_element_by_id('txtTarget').text:
        sleep(1)
    translated_text = driver.find_element_by_id('txtTarget').text
    file_write(text_file_name, translated_text)
    driver.refresh()


def file_write(filename, text):
    print("file write is called, text length : %d" % len(text))
    translated_file = open(filename, "a", encoding="utf-8")
    print(text, file=translated_file)
    translated_file.close()

if __name__ == "__main__":
    """
    네이버 뉴스기사를 수집한다.
    :return:
    """
    driver = webdriver.Chrome('/Users/Celine/Documents/Projects/Picasso/chromedriver')
    #driver = webdriver.PhantomJS('/Users/Celine/Documents/Projects/Picasso/phantomjs_macosx/bin/phantomjs')
    driver.get('http://papago.naver.com/')

    #text_file = create_text_file(text_file_name)

    input_text = ""

    date = input('type in date : ')
    text_file_name += date
    urls = get_url_list(date)
    for url in urls:
        print_url = gen_print_url(url)
        html = get_html(print_url)
        new_input = ext_body(html)
        #print("input text length : %d, new input text length : %d" % (len(input_text), len(new_input)))

        if len(input_text) + len(new_input) > 5000:
            auto_translate(input_text, driver)
            input_text = new_input
        else:
            input_text += new_input

    driver.quit()
