#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: next4nextjob@gmail.com
# Created Time: 2020年01月02日 星期四 18时46分24秒
#########################################################################
import time
import re
import requests
from bs4 import BeautifulSoup as bs
from lxml import etree
from ebooklib import epub
from ebooklib.plugins.base import BasePlugin


# 自定义CSS样式
style = '''
@namespace epub "http://www.idpf.org/2007/ops";
html, body, div, span, applet, object, iframe,
h1, h2, h3, h4, h5, h6, p, blockquote, pre, a,
abbr, acronym, address, big, cite, code, del,
dfn, em, font, ins, kbd, q, s, samp, small,
strike, strong, sub, sup, tt, var, b, u, i, center,
dl, dt, dd, ol, ul, li, fieldset, form, label, legend,
table, caption, tbody, tfoot, thead, tr, th, td {
  margin: 0;
  padding: 0;
  border: 0;
  outline: 0;
  font-size: 100%;
  vertical-align: baseline;
  background: transparent;
}

img {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
  max-width: 100%;
  height: auto;
}

div.chapter {
    page-break-after: always;
}
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, \
        Georgia, Times, Times New Roman, serif;
}
body.tp h1,
body.tp h2,
body.tp h3,
body.tp h4{
    margin:0.8rem;
    text-align:center;
}
ol {
    list-style-type: none;
}
ol > li:first-child {
    margin-top: 0.3em;
}
nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}
h1 {
    margin: 50% auto 0 0;
    font-size: 1em;
    text-align: center;
}
p {
    margin-left: 25%;
}
nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}
.symbol {
    font-family: 'DK-SYMBOL';
}
'''

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 \
    Safari/537.36'
}
default_socks = 'socks5://127.0.0.1:1081'


# 从 url 地址获取网页文本内容
def req_get_info(url, headers=None, proxies="", retry=5, timeout=15):
    '''
    发送requests请求模块，最多尝试3次
    '''
    headers = headers
    if headers is None:
        headers = default_headers
    if proxies is None:
        proxies = default_socks

    if isinstance(proxies, str):
        proxies = {
            'http': proxies,
            'https': proxies,
        }
    for _ in range(retry):
        try:
            resp = requests.get(url, proxies=proxies, headers=headers, timeout=timeout)
            print(resp.status_code, url)
            return resp
        except Exception as e:
            print('retry:', _, 'url:', url, 'proxies=', proxies, 'requests error:', str(e))
            time.sleep(0.5)
    return None


class ImagePlugin(BasePlugin):
    '''处理图片插件，自动下载图片素材到本地目录'''
    NAME = 'Image Plugin'
    url_doer = {}  # 重复URL地址记录器,同时记录文件名
    img_idx = 0    # 命名图片编号

    def __init__(self, proxy=""):
        self.proxy = proxy

    def fetch_image(self, doc, book, lable_xpath=r"//img", attr='src'):
        '''图片链接下载处理'''
        for _link in doc.xpath(lable_xpath):
            img_url = _link.get(attr)
            if not img_url.startswith('http'):
                print(f"img_url:{img_url} invalid! not startswith http")
                continue
            print(f"xpath:{lable_xpath},attr:{attr}, img_url={img_url}")
            img_url = re.sub(r'\?.*', '', img_url)     # 过滤?及其后参数请求信息#
            if self.url_doer.get(img_url) is None:
                resp = req_get_info(img_url, proxies=self.proxy)
                if resp is None:
                    print(f"Warning: image {img_url} lost!")
                    continue
                img_item = epub.EpubImage()
                file_name = '{:03d}_{}'.format(
                    self.img_idx, img_url.rsplit('/', maxsplit=1)[1]
                )
                img_item.file_name = file_name
                self.img_idx += 1
                img_item.set_content(resp.content)
                book.add_item(img_item)
                _link.set(attr, file_name)
                self.url_doer[img_url] = file_name
            else:
                print("already downloaded url:", img_url)
                file_name = self.url_doer[img_url]
                _link.set('src', file_name)
        return doc

    def html_before_write(self, book, chapter):
        '''替换图片链接地址'''
        if chapter.content is None:
            return
        doc = etree.HTML(chapter.content)
        doc = self.fetch_image(doc, book, r'//object[@class="image__image"]', 'data')
        doc = self.fetch_image(doc, book, '//img', 'src')
        chapter.content = etree.tostring(
            doc, pretty_print=True, encoding='utf-8')


class Ebook(object):
    '''
    制作电子书
    '''
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

    def set_cover(self, url):
        """设置封面"""
        return None

    def set_intro(self, content):
        """设置简介"""
        return None

    def set_proxy(self, proxy):
        """设置简介"""
        self.proxy = proxy

    def set_plugin(self, plugin):
        """设置插件"""
        self.plugin = plugin
        if self.opts.get('plugins') is None:
            self.opts['plugins'] = []
        self.opts['plugins'].append(plugin)

    def create_book(self):
        """创建ebook对象"""
        self.book = epub.EpubBook()
        self.book.set_title(self.book_name)
        self.book.add_author(self.author)
        self.book.set_language(self.lang)
        self.book.set_identifier(self.identifier)
        return self.book

    def add_chapter(self, title, file_name, content, ptype='chapter'):
        """
        生成章节内容实例
        params:
            title: 小节标题
            file_name: 保存文件名
            content: 文件内容
            ptype: 保存类型，默认为文章类型(chapter), 还可以是`image`图片类型
        return:
            chapter: 返回生成的小节对象实例
        """
        if title is None or file_name is None or content is None:
            return None
        c1 = None
        if ptype == 'chapter':
            c1 = epub.EpubHtml(title=title, file_name=file_name, lang=self.lang)
        elif ptype == 'image':
            c1 = epub.EpubImage(title=title, file_name=file_name, lang=self.lang)
        if isinstance(content, list) or isinstance(content, tuple):
            text = ""
            for line in content:
                text += "<p>" + line + "</p>\n"
            c1.set_content(text)
        else:
            c1.set_content(content)
        return c1

    def fetch_book(self):
        '''
        制作电子书主流程
        1. 获取所有章链接
        2. 按章获取所有小节链接
        '''
        book = self.create_book()
        self.set_plugin(ImagePlugin(self.proxy))
        total_toc = self.fetch_all_chapter()

        for sec in total_toc:
            book.add_item(sec)

        book.toc = tuple(total_toc)

        # add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        # add css file
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                                media_type="text/css", content=style)
        book.add_item(nav_css)

        book.spine = ['nav'] + total_toc
        book_path = f'{self.outdir}/{self.book_name}_{self.author}.epub'
        print(f'输出文件名: {book_path}')
        # opts = {'plugins': ImagePlugin(), }
        epub.write_epub(book_path, book, self.opts)

    def fetch_all_chapter(self, conf=None):
        '''
        章节内容提取器：提取所有小节内容对象实例
        params:
            conf: dict类型，包含url和level信息
            level: 提取层次，默认第0层为不区分章
            url: 访问页面地址
        return:
            list: chapter章节对象实例列表
        '''

        if conf is None:
            conf = {}
            conf['url'] = self.url
            conf['name'] = self.book_name
            conf['level'] = 0
        url = conf['url']
        level = conf['level']
        # 主页面
        total_toc = []
        resp = req_get_info(url, proxies=self.proxy)
        if resp is None:
            return None

        ch_list = self.fetch_chapter_list(resp.text)
        if len(ch_list) > 0:
            for ch_url in ch_list:
                resp1 = req_get_info(ch_url, proxies=self.proxy)
                sec_list = self.fetch_section_list(resp1.text)
                idx = 0  # 章节序号列表
                level += 1
                for sec_info in sec_list[:]:
                    stitle, surl = sec_info
                    print(f"DEBUG: {stitle}, {surl}")
                    resp2 = req_get_info(surl, proxies=self.proxy)
                    content = self.fetch_content(resp2.text)
                    chapter = self.add_chapter(stitle, 'p{:02d}_{:03d}.xhtml'.format(level, idx), content)
                    idx = idx + 1
                    total_toc.append(chapter)
        else:
            sec_list = self.fetch_section_list(resp.text)
            idx = 0  # 章节序号列表
            level += 1
            for sec_info in sec_list[:]:
                stitle, surl = sec_info
                print(f"DEBUG: {stitle}, {surl}")
                resp2 = req_get_info(surl, proxies=self.proxy)
                content = self.fetch_content(resp2.text)
                chapter = self.add_chapter(stitle, 'p{:02d}_{:03d}.xhtml'.format(level, idx), content)
                idx = idx + 1
                total_toc.append(chapter)
        return total_toc

    def fetch_chapter_list(self, content):
        '''
        抓取章(title,url)列表
        params:
            url:  访问页面URL
        return
            list  [url, ...]
        '''
        soup = bs(content, "lxml")
        # 提取章列表
        a_list = soup.select(r'div#content-list>div > h3 > a')
        return [a.get('href') for a in a_list]

    def fetch_section_list(self, content):
        '''
        抓取章/节(title,url)列表
        params:
            url:  访问页面URL
        return
            list  [(has_chapter, intro, (title, url)), ...] , has_chapter:  是否分章节,True-是，默认False
        '''
        soup = bs(content, "lxml")
        a_list = soup.select(r'div#content-list > div.book-list a')
        section_list = [(a.get('title'), a.get('href')) for a in a_list]
        return section_list

    def fetch_content(self, content):
        """
        内容提取
        params:
            url: 小节URL地址
        return:
            content: 提取内容, 默认返回整个Body体内容
        """
        try:
            soup = bs(content, 'lxml')
            content = soup.find('div', id='nr1').prettify()
            return content
        except Exception as e:
            print(str(e))
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
        ebook = Ebook(params, outdir="./")
        ebook.fetch_book()
