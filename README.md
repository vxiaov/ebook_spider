# ebook_spider
一款简单的EPUB电子书在线爬虫工具，通过简单的定制修改就可以完成博客的电子书制作。


## 使用方法

电子书的配置信息:
```python
    start_urls = [
        {
            'url': 'https://www.luoxia.com/xiaowangzi',
            'book_name': '小王子',
            'author': '[法]安托万·德·圣·埃克苏佩里',
            'id': 'xiaowangzi',
            'lang': 'zh'
        },
```
## 爬取规则自定义

### 爬取电子书章列表规则实现`fetch_chapter_list()`：
```
a_list = soup.select(r'div#content-list>div > h3 > a')
```

### 爬取每章的小节列表规则实现`fetch_section_list()`:
```
a_list = soup.select(r'div#content-list > div.book-list a')
```

### 爬取小节正文内容实现`fetch_content()`:
```
content = soup.find('div', id='nr1').prettify()
```

## 实现自己的电子书爬虫示例

我们以WordPress博客为例， 参考`wp_ebook.py`示例。

更多的示例就需要你自己动手了! 

本项目实现了图片自动下载插件，也就是当你生成电子书时图片链接会替换成下载后的图片路径。当然你也可以参考实现更多的插件来满足自己的需要。


