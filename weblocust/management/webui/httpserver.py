#coding:utf-8

import tornado.ioloop
import tornado.web    
from .urls import urlpatterns
from .websettings import configure
from weblocust.core.locusts import TornadoBaseLocust

    
def tornadoweb(port=9999):
    """
        开启web
    """
    app = tornado.web.Application(urlpatterns,**configure)
    app.listen(port)
    
    #locust = TornadoBaseLocust()
    #locust.runlocust()

    tornado.ioloop.IOLoop.current().start()

    