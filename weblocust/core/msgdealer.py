#coding:utf-8

import tornado
import tornadis
from weblocust.core import timer
from tornado.ioloop import IOLoop
from weblocust import settings

class SlaveDetector(object):
    """
        定期删除过期的slave 节点
    """
    def __init__(self):
        self._redis_client = tornadis.Client(host=settings.REDIS_SERVER,port=6379,autoconnect=True)
    
    @timer(4,3*365*24*60*60)
    @tornado.gen.coroutine    
    def __detect(self):
        """
            侦查并定期检测
        """
        nodes = yield self._redis_client.call("smembers",settings.CLUSTER_NODE_SET)
        redis_pipeline = tornadis.Pipeline()       
        
        for node in nodes:
            redis_pipeline.stack_call("hget",node,"node_info")
        
        nodes_status = yield self._redis_client.call(redis_pipeline)
        
        invalid_nodes = []

        for n in zip(nodes_status,nodes):
            if not n[0]:  #空的状态
                invalid_nodes.append(n[1])

        if invalid_nodes:
            #在有过期节点的情况下
            redis_pipeline = tornadis.Pipeline()
            [redis_pipeline.stack_call("srem",settings.CLUSTER_NODE_SET,n) for n in invalid_nodes]
            yield self._redis_client.call(redis_pipeline)
            
    def start(self):
        IOLoop.current().spawn_callback(self.__detect)
        
        