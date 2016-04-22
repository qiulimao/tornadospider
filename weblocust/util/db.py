#coding:utf-8
from weblocust.core import SigleInstance
import tornadis
from weblocust import settings
import tornado
from tornado import gen

class RedisPipeline(tornadis.Pipeline):
	pass


class RedisConnection(object):

	__metaclass__ = SigleInstance

	def __init__(self):
		self._redis_client = tornadis.Client(host=settings.REDIS_SERVER,port=6379,autoconnect=True)

	@gen.coroutine
	def call(self,*args,**kwargs):
		result  = yield self._redis_client.call(*args,**kwargs)
		raise gen.Return(result)
		

