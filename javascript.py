#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: next4nextjob@gmail.com
# Created Time: 2020年01月02日 星期四 18时46分24秒
#########################################################################

from bs4 import BeautifulSoup as bs
from Base.EbookBase import Ebook
import multiprocessing as mp


default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 \
    Safari/537.36'
}


class WebEbook(Ebook):
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
        a_list = soup.select(r'div.list > div.list__item > .list__title > a')
        section_list = []
        for a in a_list[:]:
            surl = a.get('href')
            if not surl.startswith('http'):
                surl = self.url + surl
                surl.replace(r'//', r'/')
            section_list.append(surl)
        return section_list

    def fetch_section_list(self, text):
        '''
        抓取章/节(title,url)列表
        params:
            url:  访问页面URL
        return
            list  [(title, url), ...]
        '''
        soup = bs(text, "lxml")
        # 提取小节列表
        a_list = soup.select(r'.lessons-list > ol > li > a')
        section_list = [(a.get_text().strip(), self.url + a.get('href'))
                        for a in a_list]
        return section_list

    def fetch_content(self, text):
        """
        内容提取
        params:
            url: 小节URL地址
        return:
            content: 提取内容, 默认返回整个Body体内容
        """
        reg_str = r'="/article'
        try:
            soup = bs(text, 'lxml')
            # 标题信息
            content = '<h1>' + str(soup.title) + '</h1>\n'
            # 正文内容
            content += soup.find('article').prettify()
            # 拼接为URL绝对路径
            return content.replace(reg_str, r'="' + self.url + r'/article')
        except Exception as e:
            print(str(e))
        return None


if __name__ == '__main__':
    start_urls = [
        {
            'url': 'https://zh.javascript.info',
            'book_name': '现代JavaScript教程',
            'author': 'IlyaKantor',
            'id': 'JavaScript',
            'lang': 'zh'
        },
    ]
    ctx = mp.get_context('spawn')
    p_list = []
    for params in start_urls[:]:
        ebook = WebEbook(params, outdir="./")
        p = ctx.Process(target=ebook.fetch_book)
        p.start()
        p_list.append(p)
    for p in p_list:
        p.join()
