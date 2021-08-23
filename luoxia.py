#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zwker
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年01月02日 星期四 18时46分24秒
#########################################################################

import re
from bs4 import BeautifulSoup as bs
from Base.EbookBase import Ebook


class LuoxiaEbook(Ebook):
    # 电子书制作
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
            content = soup.find('div', id='nr1').prettify()
            # 过滤网站水印
            content = re.sub(r'.*?落.*?霞.*?小.*?[说說].*', '', content)
            return content
        except Exception as e:
            pass
        return None


if __name__ == '__main__':
    start_urls = [
        {
            'url': 'https://www.luoxia.com/xiaowangzi',
            'book_name': '小王子',
            'author': '[法]安托万·德·圣·埃克苏佩里',
            'id': 'xiaowangzi',
            'lang': 'zh'
        },
        {
            'url': 'https://www.luoxia.com/haibolian',
            'book_name': '海伯利安',
            'author': '[美]丹·西蒙斯',
        },
    ]
    for params in start_urls[:]:
        ebook = LuoxiaEbook(params, outdir="./")
        ebook.fetch_book()
