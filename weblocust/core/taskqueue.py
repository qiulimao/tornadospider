#coding:utf-8

from tornado import httpclient,gen,ioloop,queues
from . import SigleInstance
import tornadis 
from .httpclient import Request
import json

class TaskQueue(object):
    """
    all task queue derive from this class
    """
    #__metaclass__ = SigleInstance
    

    def get(self):
        raise NotImplementedError

    def put(self,request):
        raise NotImplementedError
    
        
        
class NormalTaskQueue(TaskQueue):
    """
    this queue use tornado built in queue,since we need an asychronous queue;
    
    """

    def __init__(self):
        self.queue = queues.Queue()


    @gen.coroutine
    def get(self):
        task = yield self.queue.get()
        raise gen.Return(task)
    
    @gen.coroutine
    def put(self,request):
        ack = yield self.queue.put(request)
        raise gen.Return(ack)

    
class RedisTaskQueue(TaskQueue):
    """
    this queue use redis the memory database;by this way ,
    this framework turn into a distribute system be possible
    """
    def __init__(self,host="localhost",port=6379):
        """
        为了和其它queue初始化一样，这里初始化传入的参数应该尽量做到一致
        """
        self.client = tornadis.Client(host="localhost",port=6379,autoconnect=True)
    
    @gen.coroutine    
    def get(self):
        """
        get a request instance from queue
        """
        r = yield self.client.call("LPOP","request_queue")
        while not r:
            # 没有任务的情况下肯定会阻塞，所以暂时交出控制权
            # 只有一条redis链接，这里要是阻塞了，所有的都会阻塞。所以没有用BLPOP
            yield gen.sleep(1)
            r = yield self.client.call("LPOP","request_queue")
            
            
        if isinstance(r,tornadis.TornadisException):
            # 发生exceptions 的情况下，返回None
            # 或者直接raise一个exception
            print "got exception: %s " % r
            raise gen.Return(None)

        #反序列化，恢复Request    
        req = json.loads(r)
        request = Request(**req)
        raise gen.Return(request)
        
    @gen.coroutine    
    def put(self,request):
        """ 
        put request's attribute to queue 
        since we can't push a python instance to redis,
        we have to make all attribute to string
        fortunately,json.dumps make dict to string,and instance's attributes
        stores in instance.__dict__
        """
        r = request.__dict__
        req = json.dumps(r)
        ack = yield self.client.call("rpush","request_queue",req)
        raise gen.Return(ack)
        
