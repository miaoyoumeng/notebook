import requests
from bs4 import BeautifulSoup
import html2text as ht

## 针对网址https://pdai.tech/转化为markdown内容

# 此处写你要爬虫的url
url = 'https://pdai.tech/md/db/nosql-redis/db-redis-y-monitor.html'

#爬虫
res = requests.get(url)
data = res.content
cont = BeautifulSoup(data, 'html.parser')
#获取包含文章内容的标签 attrs后跟的是最外层标签属性，根据爬取网站的实际情况进行修改

# data = cont.find('//*[@id="app"]/div/main/div[1]/div').text
markdownHtml = cont.find('div',attrs={'class':'theme-default-content'})

html = str(markdownHtml)

#对上述字符串data进行处理，去除不能转换成markdown的标签，比如div等
#该部分代码根据需要自行添加，此处不给出

#转换
# text_maker = ht.HTML2Text()
# text_maker.bypass_tables = False
# text = text_maker.handle(data)
text = ht.html2text(html)

# #对获取的md格式的文本进行操作，比如写入到一个文件中，此处作为演示直接输出
print(text)