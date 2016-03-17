#coding:utf-8

import time 
import random
from socket import gaierror
from datetime import timedelta 
from HTMLParser import HTMLParser
from urlparse import urljoin,urldefrag 
from tornado import httpclient,gen,ioloop,queues
from tornado.ioloop import IOLoop

from weblocust.core import timer,crontab
from tornado.httpclient import HTTPRequest,HTTPResponse
from tornado.httputil import HTTPHeaders

from .httpclient import TornadoRequestBuilder,TornadoHttpclientHeaderManager
from .httpclient import WebLocustRequest,TornadoResponse

from .taskqueue import *

class BaseLocut(object):
    """
    """
    start_urls = []
    
    def request(self,url):
        """
        """
        raise NotImplementedError

class TornadoBaseLocust(BaseLocut):
    """
        基本
        Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36
        cookie：的基本样子：
        ['__cfduid=d91d42345b0e1eacce8110aa7a67e0b111458022618; expires=Wed, 15-Mar-17 06:16:58 GMT; path=/; domain=.wooyun.org; HttpOnly', 'PHPSESSID=i7sm27865ja25o0ba516vd9fi5; path=/']

    """
    start_url = "http://news.163.com/"
    start_urls = ["http://news.163.com/","http://www.163.com/"]
    cookie = None
    concurrency = 16
    header_manager = TornadoHttpclientHeaderManager()
    
    COOKIE_ENABLE = False
    
    count = 0

    Load_factor = 0
    
    def __init__(self):
        self.before_start()
    
    def handle_cookie(self,response,froce = False):
        """
            处理cookie问题
        """
        if self.COOKIE_ENABLE:
            self.header_manager.add_cookie(response.headers.get_list("Set-Cookie"))
        elif froce:
            self.header_manager.add_cookie(response.headers.get_list("Set-Cookie"))
    

    def before_start(self):
        """
            这个函数必须让他阻塞，因为它带回cookie，后面才能继续操作
            有个问题是：
                启动的时候，这个方法只需要执行一次，并不是每次定时启动时都要经历这个步骤。
                所以，最好就是：开始启动时就执行一次，以后都不要执行了。
            所以实例化这个类的时候，直接调用这个函数。
            
            ##
            #要不要把start_urls里面的url都访问一遍ne?
            #
        """
        request = TornadoRequestBuilder.build_request(self.start_url)

        response =  httpclient.HTTPClient().fetch(request)

        self.handle_cookie(response,froce = True)
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>"
        return response
        
    @gen.coroutine
    def visit(self,url):
        """
            访问某个网页
        """
        request = TornadoRequestBuilder.build_request(url)
        try:
            response = yield httpclient.AsyncHTTPClient().fetch(request)  
            #print "successfully request the url %d" % random.randrange(1,100)
            
            self.handle_cookie(response)
            
            raise gen.Return(response)    
        
        except gen.Return:
            raise gen.Return(response)       
        except httpclient.HTTPError as e:
            print "suffered an http error[%s]" % e
            print url
        except gaierror as e:
            print "get an socket error[gaierror]"
        except Exception as e:
            print "get an [%s] error" % type(e)
        
        self.count += 1
        #self.Load_factor += 1
    @gen.coroutine
    def consumer(self):
        """
            调度程序
        """
        while True:    
            task = yield self.get_from_queue()            
            response = yield self.visit(task.url)
            NormalTaskQueue.queue.task_done()
            self.Load_factor += 1  
            
            if not isinstance(response,HTTPResponse):
                continue        
            yield getattr(self,task.callback)(TornadoResponse(response))   
             
    @gen.coroutine
    def start_consumers(self):
    
        for _ in range(self.concurrency):
            yield self.consumer()
    
    @gen.coroutine
    def parse(self,response):
        """
            解析和存储过程不能使用异步，因为：
                普通情况下操作文件可以使用异步，但是因为是数据库操作，
                所以很有可能造成数据库锁表，因此效率会更加大打折扣。
        """

        links =  response.xpath("//a/@href")
        
        for link in links:
            yield self.send_request(WebLocustRequest(link,"parse_one"))
    
    @gen.coroutine
    def parse_one(self,response):
        print response.request_time,response.url
        #print response.xpath("//title/text()")
    
    @timer(interval=5,lifespan=10*356*24*60*60)
    @gen.coroutine
    def status_watcher5s(self):
        for _ in range(self.Load_factor):
            print "-",
        print self.Load_factor 
        self.Load_factor = 0  
    
    #@gen.coroutine
    #def status_watcher(self):
    #    for _ in range(self.Load_factor/5):
    #        print "-",
    #    print self.Load_factor 
    #    self.Load_factor = 0          
     
    #@timer(interval=1*60*60,lifespan=200)
    @gen.coroutine
    def start(self):
        """
            启动爬虫程序
        """
        self.count += 1
        
        #往队列当中构造任务
        for url in self.start_urls:
            yield self.put2queue(WebLocustRequest(url,"parse"))
    
    
    @gen.coroutine
    def put2queue(self,request):
        ack = yield NormalTaskQueue.put(request)
        raise gen.Return(ack)
        
    @gen.coroutine
    def send_request(self,request):
        ack = yield self.put2queue(request)
        raise gen.Return(ack)
    
    @gen.coroutine    
    def get_from_queue(self):
        task = yield NormalTaskQueue.get()
        raise gen.Return(task)
               
    def addto_noblocking(self):
        IOLoop.current().spawn_callback(self.start)
        IOLoop.current().spawn_callback(self.start_consumers)
        IOLoop.current().spawn_callback(self.status_watcher5s)