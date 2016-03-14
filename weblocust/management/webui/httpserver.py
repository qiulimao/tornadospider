#coding:utf-8

import tornado.ioloop
import tornado.web    
from .urls import urlpatterns
from .websettings import configure
from weblocust.core.locusts import BaseLocust

    
def tornadoweb(port=9999):
    """
        开启web
    """
    app = tornado.web.Application(urlpatterns,**configure)
    app.listen(port)
    locust = BaseLocust()
    locust.addto_noblocking()
    tornado.ioloop.IOLoop.current().start()
    