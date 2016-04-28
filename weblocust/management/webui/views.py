
#coding:utf-8
import json 
import urllib 

import tornado
import random
from weblocust.core.locusts import TornadoBaseLocust

import tornadis 
from tornado.escape import json_encode
from weblocust.util.serialize import SqlAlchemyEncoder

from weblocust import settings
from weblocust.util.db import RedisConnection,RedisPipeline
from weblocust.master.node import Slave 

class MainHandler(tornado.web.RequestHandler):
    """
        控制台,总控制页面
    """
    def get(self):
        context = {
            'title':"tornado web framework with angularjs",
            'items':('a','b','c'),
            'message':"hello,world %d" % random.randrange(1,100),
        }
                
        self.render('main/index.html',**context)
    

        
        
class InfoCenter(tornado.web.RequestHandler):
    """
        接收所有来自其它节点的信息，并做持久化;
        提供机群的信息
        代理administrator发出命令和请求
        一次更新所有能够获知的信息

        ##
        # http://localhost:999/infocenter
        ##
    """
        
    @tornado.gen.coroutine
    def get(self):
        """
            提供整个集群的信息
            请求地址：/infocenter
        """
        all_slaves = Slave.roster.all()

        sysinfo = {
            "tooken":random.randrange(1,10000),
            "nodes":json.dumps(all_slaves,cls=SqlAlchemyEncoder),
        }
        

        for slave in all_slaves:

            print slave.ip,"\t",slave.port,"\t",slave.init_time,"\t",slave.update_time,"\t"
            
        self.write(sysinfo)
        self.finish()
        
    @tornado.gen.coroutine           
    def post(self):
        """
           接收slave发过来的节点数据，并将写到roster当中
           /infocenter 
        """

        #----database persist node status
        ip = self.get_body_argument("ip")
        port = self.get_body_argument("port")

        status = {
            "role":self.get_body_argument("role"),
            "state_running":1 if self.get_body_argument("running")=="True" else 0,
            "state_working":1 if self.get_body_argument("working")=="True" else 0,
            "state_workload":self.get_body_argument("load_factor"),
            "state_qsize":self.get_body_argument("qsize"),
        }

        slavenode = Slave(ip,port)
        echo = slavenode.greeting(status)
        cmds = {
            "running":echo.cmd_running,
            "working":echo.cmd_working,
        }
        #print json.dumps(echo,cls=SqlAlchemyEncoder)

        self.write(json.dumps(cmds))
        self.finish()
        
class LocustController(tornado.web.RequestHandler):
    """
        地址为：http://localhost:9999/locust-control
    """
            
    def get(self):
        """
            获取所有的提交数据：
                self.request.body

            post format:
            {
                action:"start",
                _ip:"192.168.0.1",
                _port:"8080",
            }
        """

        operation = self.get_query_argument("action")

        if hasattr(self,operation):
            ip = self.get_query_argument("ip")
            port = self.get_query_argument("port")
            self.__slave = Slave(ip,port)

            if not self.__slave.exists():
                reply = {"error":1,"msg":u"the slave node {0}:{1} does not exist".format(ip,port)}
                self.write(reply)
                self.finish()
                return 
                
            reply = getattr(self,operation)()
        else:
            reply = {"error":1,"msg":"errors"}
            
        self.write(reply)
        self.finish()
            
    def start(self):
        self.__slave.start()
        return {"error":0,"smg":"start the locust"}
    
    def restart(self):
        self.__slave.stop()
        return {"error":0,"smg":"start the locust"}
    
    def pause(self):
        self.__slave.pause()
        return {"error":0,"smg":"pause the locust"}        
        
    def resume(self):
        self.__slave.resume()
        return {"error":0,"smg":"pause the locust"}