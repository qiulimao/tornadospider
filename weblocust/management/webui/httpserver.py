#coding:utf-8

import tornado.ioloop
import tornado.web    
from .urls import urlpatterns
from .websettings import configure
from weblocust.core.locusts import TornadoBaseLocust
from weblocust.core.plugin import ZombieSlaveDetector
    
def tornadoweb(port=9999):
    """
        开启web
    """
    locust_controller = tornado.web.Application(urlpatterns,**configure)
    locust_controller.listen(port)
    ZombieSlaveDetector().start()
    #tornado.ioloop.IOLoop.current().start()

    