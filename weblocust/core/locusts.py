#coding:utf-8

import time 
from datetime import timedelta 
from HTMLParser import HTMLParser
from urlparse import urljoin,urldefrag 
from tornado import httpclient,gen,ioloop,queues
from tornado.ioloop import IOLoop

from weblocust.core import timer,crontab

class BaseLocust(object):
    """
        基本
    """
    start_url = "http://www.wooyun.org"
    
    
    @gen.coroutine
    def request(self,url):
        response = yield httpclient.AsyncHTTPClient().fetch("http://www.wooyun.org")
        print "fetch a page"
        raise gen.Return(response)
          
    @timer(interval=2,lifespan=20)
    @gen.coroutine
    def start(self):
        """
        """
        self.request(self.start_url)
          
    def addto_noblocking(self):
        IOLoop.current().spawn_callback(self.start)