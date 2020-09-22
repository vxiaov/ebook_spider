#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: next4nextjob@gmail.com
# Created Time: 2020年01月02日 星期四 18时46分24秒
#########################################################################

import re
from bs4 import BeautifulSoup as bs
from ebook_spider import Ebook
import requests
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing as mp


default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 \
    Safari/537.36'
}


class WordPressEbook(Ebook):
    # 电子书制作
    def __init__(self, params, outdir="./", proxy=""):
        if not isinstance(params, dict):
            raise TypeError("params type error! not dict type.")
        self.url = params['url']
        self.book_name = params['book_name']
        self.author = params['author']
        self.lang = params.get('lang', 'zh')
        self.identifier = params.get('id', 'id0001')
        self.outdir = outdir
        self.proxy = proxy
        self.opts = {}
        self.plugin = None

    def fetch_chapter_list(self, text):
        '''
        抓取章url列表
        params:
            text:  章列表的HTML页面
        return
            list  [url, ...]
        '''
        soup = bs(text, "lxml")
        # 提取章列表
        section_list = []
        return section_list

    def fetch_section_list(self, text):
        '''
        抓取章/节(title,url)列表
        params:
            url:  访问页面URL
        return
            list  [(has_chapter, intro, (title, url)), ...] , has_chapter:  是否分章节,True-是，默认False
        '''
        soup = bs(text, "lxml")
        # 提取小节列表
        a_list = soup.select(r'nav > ul > li.chapter > a')
        # 提取书/章节描述信息(用于生成简介)
        section_list = [(a.get_text().encode('iso8859-1').decode('utf-8').strip(), self.url + '/' + a.get('href')) for a in a_list[3:]]
        print(section_list)
        return section_list

    def fetch_content(self, text):
        """
        内容提取
        params:
            url: 小节URL地址
        return:
            content: 提取内容, 默认返回整个Body体内容
        """
        try:
            soup = bs(text, 'lxml')
            content = '<h1>' + str(soup.title) + '</h1>\n'
            content = soup.find('section').prettify()
            return content
        except Exception as e:
            print(str(e))
        return None


if __name__ == '__main__':
    start_urls = [
        {
            'url': 'https://book.8btc.com/books/6/masterbitcoin2cn/_book/',
            'book_name': '精通比特币',
            'author': '8bit',
            'id': '8bit',
            'lang': 'zh'
        },
    ]
    ctx = mp.get_context('fork')
    p_list = []
    for params in start_urls[:]:
        ebook = WordPressEbook(params, outdir="./")
        p = ctx.Process(target=ebook.fetch_book)
        p.start()
        p_list.append(p)
    for p in p_list:
        p.join()
