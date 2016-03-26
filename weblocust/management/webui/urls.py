#coding:utf-8
import views 
from tornado.web import url

urlpatterns = [
            url(r'/',views.MainHandler,name='home_page'),
            url(r'/infocenter',views.InfoCenter,name="infocenter"),
            url(r'/locust-control',views.LocustController,name="lcst_ctl"),
        ]