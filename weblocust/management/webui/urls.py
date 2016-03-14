#coding:utf-8
import views 
from tornado.web import url

urlpatterns = [
            url(r'/',views.MainHandler,name='home_page'),
        ]