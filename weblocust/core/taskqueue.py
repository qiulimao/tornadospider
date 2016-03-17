#coding:utf-8

from tornado import httpclient,gen,ioloop,queues
from . import SigleInstance

class TaskQueue(object):
    """
    """
    __metaclass__ = SigleInstance
    
    @classmethod
    def get(self):
        pass
        
    @classmethod 
    def put(self,request):
        pass
        
        
class NormalTaskQueue(TaskQueue):
    """
    """

    queue = queues.Queue()

    
    @classmethod
    @gen.coroutine
    def get(cls):
        task = yield cls.queue.get()
        cls.current_task = task
        raise gen.Return(task)
    
    @classmethod 
    @gen.coroutine
    def put(cls,request):
        ack = yield cls.queue.put(request)
        raise gen.Return(ack)
    
    @classmethod    
    @property
    def current_task(cls):
        return cls.current_task
    
    @classmethod
    @property    
    def current_task(cls,task):
        cls.current_task = task
    
    