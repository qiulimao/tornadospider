
#coding:utf-8

import tornado
import random
from weblocust.core.locusts import TornadoBaseLocust
import json 
import tornadis 

class MainHandler(tornado.web.RequestHandler):
    """
        控制台
    """
    def get(self):
        context = {
            'title':"tornado web framework with angularjs",
            'items':('a','b','c'),
            'message':"hello,world %d" % random.randrange(1,100),
        }
        
        #TornadoBaseLocust().current().runlocust()
        
        self.render('main/index.html',**context)
    
    #@tornado.web.authenticated
    def post(self,operation,id):
        """
        append_node = {
            "role":"slave",
            "ip":"10.0.1.1",
            "port":988,
            "qps":10,
            "is_started":True,
            "is_paused":True,        
        }
        print self.request.body
        """
        
        
        if hasattr(self,operation):
            reply =  getattr(self,operation)(id)
        else:
            reply = {"error":1,"msg":"no such operation"}
            
        self.write(json.dumps(reply))
        
    def locust_pause(self,id):
        """
        """
        TornadoBaseLocust().current().pause()
        return {"error":0,"msg":"paused the locust"}
        
    def locust_resume(self,id):
        """
        """
        TornadoBaseLocust().current().resume()
        return {"error":0,"msg":"resumed the locust"}
    
    def locust_start(self,id):
        TornadoBaseLocust().current().runlocust()
        return {"error":0,"msg":"start the locust"}


class SysInfoHandler(tornado.web.RequestHandler):
    """
    """
    def initialize(self):
        """
            拿到redis的链接
        """
        self.redis_client = tornadis.Client(host="localhost",port=6379,autoconnect=True)
    
    @tornado.gen.coroutine      
    def get(self):
        """
        """
        queue_length = yield self.redis_client.call("llen","request_queue")

  
        self.write(json.dumps({
            "queue_length":queue_length,
        }))
 
        self.finish()
        
        