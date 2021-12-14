#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: next4nextjob@gmail.com
# Created Time: 2020年01月02日 星期四 18时46分24秒
#########################################################################


from bs4 import BeautifulSoup as bs
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing as mp
import re

from Base.EbookBase import Ebook,req_get_info


default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 \
    Safari/537.36'
}




class WenXue88Ebook(Ebook):
    # 电子书制作

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
        a_list = soup.select(r'a')
        # 提取书/章节描述信息(用于生成简介)
        section_list = [(a.get_text(), self.url + "/" + a.get('href')) for a in a_list if a.get('href')[0:2] == "xb"]
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
            content = soup.find_all('td', class_="hycolor")[1].prettify()
            return content
        except Exception as e:
            pass
        return None


if __name__ == '__main__':
    start_urls = [
        {
            'url': 'http://wenxue88.com/xuebeng',
            'page_num': 1,
            'book_name': '雪崩',
            'author': '尼尔·斯蒂芬森',
            'id': 'snowcrash',
            'lang': 'zh'
        },
    ]
    for params in start_urls[:]:
        ebook = WenXue88Ebook(params, outdir="./")
        ebook.fetch_book()
