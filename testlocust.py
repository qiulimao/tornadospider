#coding:utf-8
from weblocust.core.locusts import TornadoBaseLocust
from tornado import gen
from weblocust.core.httpclient import Request
from weblocust.management import NodeSettings
import settings 
from weblocust import settings as default_settings

class TestLocust(TornadoBaseLocust):

    name="test_locust"

    start_urls = [
        "http://news.163.com/",
        "http://www.163.com/",
        "http://news.sina.com.cn/",
        "http://news.baidu.com/",
        "http://news.qq.com/",
        "http://news.ifeng.com/"
        "http://www.wooyun.org"
        ]

    @gen.coroutine
    def parse(self,response):
        """
            解析和存储过程不能使用异步，因为：
                普通情况下操作文件可以使用异步，但是因为是数据库操作，
                所以很有可能造成数据库锁表，因此效率会更加大打折扣。
            所有的请回回调函数都是 producer
        """

        links =  response.xpath("//a/@href")
        
        yield [self.send_request(Request(
                                        response.urljoin(link),
                                        cookie = response.cookie,
                                        callback="parse_one")
                                ) for link in links]
    
    @gen.coroutine
    def parse_one(self,response):
        a = response.xpath("//title/text()")
        if a:
            print a[0]

if __name__ =="__main__":
    
    NodeSettings.configure(**settings.configure)
    TestLocust().prepare()