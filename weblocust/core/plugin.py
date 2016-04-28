#coding:utf-8

import tornado
import tornadis
from weblocust.core import timer
from tornado.ioloop import IOLoop
from weblocust import settings
from weblocust.util.db import RedisConnection,RedisPipeline
from weblocust.master.node import Slave
from weblocust import settings 


class ZombieSlaveDetector(object):

    @timer(settings.DETECT_ZOMBIE_FRENQUENCY,0)
    @tornado.gen.coroutine
    def __detect(self):
        Slave.remove_zombies()

    def start(self):
        IOLoop.current().spawn_callback(self.__detect)

