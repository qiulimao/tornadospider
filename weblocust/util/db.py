#coding:utf-8
from weblocust.core import SigleInstance
import tornadis
from weblocust import settings
import tornado
from tornado import gen

class RedisPipeline(tornadis.Pipeline):
	"""
		just a simple wrapper for tornadis.Pipeline
	"""
	pass


class RedisConnection(object):
	"""
		offer and singlenton RedisConnection,

	"""
	__metaclass__ = SigleInstance

	_redis_client = tornadis.Client(host=settings.REDIS_SERVER,port=6379,autoconnect=True)


	@gen.coroutine
	def call(self,*args,**kwargs):
		result  = yield self._redis_client.call(*args,**kwargs)
		raise gen.Return(result)

	@classmethod
	@gen.coroutine
	def call(cls,*args,**kwargs):
		"""
			class method `RedisConnection.call` is available to avoid mistakes;
			you can use:
				RedisConnection().call('llen','task_queue')
			the way below is also feasible and it is the recommanded way :
				RedisConnection.call('llen','task_queue')

		"""
		result = yield cls._redis_client.call(*args,**kwargs)
		raise gen.Return(result)
		

