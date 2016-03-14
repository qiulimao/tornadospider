
#coding:utf-8

import tornado
import random

class MainHandler(tornado.web.RequestHandler):
    """
        控制台
    """
    def get(self):
        context = {
            'title':"tornado web framework with angularjs",
            'items':('a','b','c'),
            'message':"hello,world %d" % random.randrange(1,100),
        }
        
        
        self.render('main/index.html',**context)
    
    @tornado.web.authenticated
    def post(self):
        pass