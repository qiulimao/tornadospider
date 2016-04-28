#coding:utf-8
# weblocust naming rules:
#   instance attribute type       instance_attribute 
#   instance method type          instance_method
#   class attribute               class_attribute 
#   class method                  class_method
#   method and attribute that not recommanded to use in client code    _instance_method


import time 
import random
import traceback
import importlib
import commands
import tornadis 
import urllib 
import json

from socket import gaierror
from datetime import timedelta 
from HTMLParser import HTMLParser
from urlparse import urljoin,urldefrag 
from tornado import httpclient,gen,ioloop,queues
from tornado.ioloop import IOLoop

from weblocust import settings
from weblocust.core import timer,crontab
from tornado.httpclient import HTTPRequest,HTTPResponse
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httputil import HTTPHeaders

from .httpclient import TornadoResponseBuilder,Request,Build2TornadoRequest
from .taskqueue import *
from . import SigleInstance



CurlAsyncHTTPClient.configure(None, defaults=dict(max_clients=200))

        

class TornadoBaseLocust(object):
    """
        基于tornado的爬虫父类
        以 "_" 开头的方法客户端代码尽量不要调用，这些代码为框架调用
    """
    
    name = "tornado_base_locust"

    start_urls = []
   
    task_queue_type = "RedisTaskQueue"      # 这个设计有点丑陋，任务队列的配置文件应该写在配置文件当中
    
    __load_factor = 0

    _working = False

    _running = False
    
    def __init__(self):

        queuelib = importlib.import_module("weblocust.core.taskqueue")
        
        self._taskqueue = getattr(queuelib,self.task_queue_type)(self.name)

        self._ip = commands.getoutput("hostname -I").strip()
        self._port = random.randrange(1000,65535)
        self.before_start()
             
    @gen.coroutine
    def _visit(self,request):
        """
            访问某个网页
            request 必须是一个 weblocust.core.httpclient.Request
        """
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
    def _consumer(self):
        """
            消费者
            首先从队列当中获得请求
            将请求转换为tornado当中的请求
            访问页面，收到response
        """
        while True:
            try:    
                request = yield self._get_from_queue()
                if not isinstance(request,Request):
                    """ filter out illegal request """
                    print "Request instance requried,rather than %s" % type(request)
                    continue
                
                tornado_request = Build2TornadoRequest.build_request(request)
                tornado_response = yield self._visit(tornado_request)
                self.__load_factor += 1  
                
                if not isinstance(tornado_response,HTTPResponse):
                    """ filter out illegal response """
                    print "we need HTTPResponse instance from[%s],not [%s]" % (request.url,type(tornado_response))
                    continue
                
                response = TornadoResponseBuilder.build_response(tornado_response)
                yield getattr(self,request.callback)(response) 
            except Exception as e:
                print "[FatalError] %s" % traceback.format_exc()
             
    @gen.coroutine
    def _start_consumers(self):
        """
            批量的异步作业时，需要一起yield，否则第一个任务阻塞了，后面的任务都没法加入ioloop
            但是有个问题：
            如果一起yield，如果list当中的任何一个yield发生exception，将不会被及时抛出！！！
            所以最好在每个协程里面处理异常
        """
        yield [self._consumer() for _ in range(settings.CONCURRENCY)]


    @timer(interval=settings.STATUS_WATCHER_FRENQUENCY,lifespan=0)
    @gen.coroutine
    def _status_watcher(self):
        """
            这个函数在初始化的时候就已经被调用了
            每5s的任务情况统计器
            nodeinfo:
            {
                "ip":"192.168.0.1",
                "port":90,
                "role":"slave",

                "state_running":1     # the locust is running,but may not working
                "state_working":1     # the locust is working fecting and parsing
                "state_workload":32   # the workload per second
                "state_qsize":1231    # current queue size 

            }
        """
        qsize = yield self._taskqueue.qsize()

        node_info = {
            "role":"master" if self._ip == settings.MASTER_ADDRESS else "slave",
            "running":self._running ,
            "working":self._working,
            "load_factor":self.__load_factor/settings.STATUS_WATCHER_FRENQUENCY,
            "ip":self._ip,
            "port":self._port,
            "qsize":qsize
        }
        
        request= HTTPRequest("http://%s:%d/infocenter" % (settings.MASTER_ADDRESS,settings.MASTER_PORT),\
            method="POST",body=urllib.urlencode(node_info))

        resp = yield CurlAsyncHTTPClient().fetch(request)   
        cmds = json.loads(resp.body)

        self._cmd_working(cmds.get("working",False))
        self.__load_factor = 0 

    def _cmd_working(self,cmd):
        self._working = True if cmd else False

    #@timer(interval=1*10,lifespan=300)
    @gen.coroutine
    def _start_task(self):
        """
            添加初始任务，slave 节点不应该调用这个方法
        """       
        #往队列当中构造任务
        yield [self._put2queue(Request(url,callback="parse")) for url in self.start_urls]
    
        
    @gen.coroutine
    def _put2queue(self,request):
        """
        封装往队列中添加任务
        """
        ack = yield self._taskqueue.put(request)
        raise gen.Return(ack)
          
    @gen.coroutine    
    def _get_from_queue(self):
        """
        封装从queue当中获取任务
        """
        while not self._working:
            yield gen.sleep(3)
            
        task = yield self._taskqueue.get()
        raise gen.Return(task)

    def crontab(self):
        pass

    def prepare(self):
        IOLoop.current().spawn_callback(self._status_watcher)
        IOLoop.current().spawn_callback(self._start_task)
        IOLoop.current().spawn_callback(self._start_consumers)
        IOLoop.current().start()
        
    def current(self):
        """ """
        return self._instance
      
    @gen.coroutine
    def send_request(self,request):
        """
        功能和 self._put2queue一样，只是这个函数封装给客户端代码调用
        """
        ack = yield self._put2queue(request)
        raise gen.Return(ack)
        
        
    def before_start(self):
        """
            start before the locust works,you may use it for login,and get the cookie
        """
        pass
            
    @gen.coroutine
    def parse(self,response):
        """
        """
        raise NotImplementedError

               
