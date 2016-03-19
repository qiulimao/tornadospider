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
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httputil import HTTPHeaders

from .httpclient import TornadoRequestBuilder,TornadoHttpclientHeaderManager
from .httpclient import WebLocustRequest,TornadoResponseBuilder,Request,Build2TornadoRequest

from .taskqueue import *
import traceback


CurlAsyncHTTPClient.configure(None, defaults=dict(max_clients=200))

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
        基于tornado的爬虫父类
    """
    start_url = "http://news.163.com/"
    start_urls = [
        #"http://news.163.com/",
        #"http://www.163.com/",
        #"http://news.sina.com.cn/",
        #"http://news.baidu.com/",
        #"http://news.qq.com/",
        #"http://news.ifeng.com/"
        "http://www.wooyun.org"
        ]
    concurrency = 64
    
    header_manager = TornadoHttpclientHeaderManager()
    
    COOKIE_ENABLE = False
    
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
            ##
        """
        request = TornadoRequestBuilder.build_request(self.start_url,self.header_manager.headers)
        response =  httpclient.HTTPClient().fetch(request)
        self.handle_cookie(response)
        return response
        
    @gen.coroutine
    def visit(self,request):
        """
            访问某个网页
        """
        #request = TornadoRequestBuilder.build_request(url,self.header_manager.headers)
        try:
            response = yield CurlAsyncHTTPClient().fetch(request)                               
            raise gen.Return(response)            
        except gen.Return:
            raise gen.Return(response)       
        except httpclient.HTTPError as e:
            print "http error[%s]" % e
        except gaierror as e:
            print "gai error"
        except Exception as e:
            print "error %s" %e 

        
    @gen.coroutine
    def consumer(self):
        """
            消费者
        """
        while True:
            try:    
                request = yield self.get_from_queue()            
                response = yield self.visit(Build2TornadoRequest.build_request(request))
                NormalTaskQueue.queue.task_done()
                self.Load_factor += 1  
                if not isinstance(response,HTTPResponse):
                    print "we need HTTPResponse instance from[%s],not [%s]" % (request.url,type(response))
                    continue
                locust_response = TornadoResponseBuilder.build_response(response)            
                yield getattr(self,request.callback)(locust_response) 
            except Exception as e:
                print "[FatalError] %s" % traceback.format_exc()
             
    @gen.coroutine
    def start_consumers(self):
        """
            批量的异步作业时，需要一起yield，否则第一个任务阻塞了，后面的任务都没法加入ioloop
            但是有个问题：
                如果一起yield，如果list当中的任何一个yield发生exception，将不会被及时抛出！！！
                <所以最好在每个协程里面处理异常>
        """
        yield [self.consumer() for _ in range(self.concurrency)]
    
    @gen.coroutine
    def parse(self,response):
        """
            解析和存储过程不能使用异步，因为：
                普通情况下操作文件可以使用异步，但是因为是数据库操作，
                所以很有可能造成数据库锁表，因此效率会更加大打折扣。
            所有的请回回调函数都是 producer
        """

        links =  response.xpath("//a/@href")
        yield [self.send_request(Request(response.urljoin(link),callback="parse_one")) for link in links]
    
    @gen.coroutine
    def parse_one(self,response):
        #print response.request_time,response.url
        #print response.xpath("//title/text()")
        #links =  response.xpath("//a/@href")
        #yield [self.send_request(WebLocustRequest(link,"final_page")) for link in links]
        a = response.xpath("//title/text()")
        if a:
            print "\t",response.url,"\t",a[0]   
        else:
            print "###############################################################"

            
            
    @gen.coroutine
    def final_page(self,response):
        """
            producer
        """
        pass
    
    @timer(interval=5,lifespan=10*356*24*60*60)
    @gen.coroutine
    def status_watcher5s(self):
        """
            每5s的任务情况统计器
        """
        for _ in range(self.Load_factor/5):
            print "-",
        print self.Load_factor/5 
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
        #往队列当中构造任务
        #for url in self.start_urls:
        #    yield self.put2queue(WebLocustRequest(url,"parse"))
        #
        yield [self.put2queue(Request(url,callback="parse")) for url in self.start_urls]
    
    
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