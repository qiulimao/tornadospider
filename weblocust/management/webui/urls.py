#coding:utf-8
import views 
from tornado.web import url

urlpatterns = [
            url(r'/',views.MainHandler,name='home_page'),
            url(r'/(?P<operation>\w+)/(?P<id>\d{1})',views.MainHandler,name='node_operate'),
            url(r'/sysinfo',views.SysInfoHandler,name="sysinfo"),
        ]