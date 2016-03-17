#coding:utf-8
from . import SigleInstance
from tornado.httputil import HTTPHeaders
from tornado.httpclient import HTTPRequest
import lxml.html


class WebLocustRequest():
    def __init__(self,url,callback):
        self.url = url
        self.callback = callback

class RequestBuilder(object):
    """
    """
    #__metaclass__ = SigleInstance
    
    @classmethod
    def build_request(cls,url,cookie=None):
        """
            返回一个request对象
        """
        raise NotImplementedError

class TornadoRequestBuilder(RequestBuilder):
    """
    """
    @classmethod
    def build_request(cls,url):
        return HTTPRequest(url,headers=TornadoHttpclientHeaderManager().headers,follow_redirects=True,max_redirects=3)
            

class HeaderBuilder(object):
    """
        是否应该使用单列模式呢？
        如果整个ioloop当中仅仅只有一只爬虫在运行，那么无所谓
        如果有多只爬虫在跑，那么将会造成cookie等东西混乱
    """
    #__metaclass__ = SigleInstance
    
    def build_header(cls,user_agent,cookie):
        """
            应该就需要userage 和cookie
        """
        raise NotImplementedError
        
    def add_cookie(self,cookie):
        """
        """
        raise NotImplementedError
        
    def alter_useragent(self,user_agent):
        """
        """
        raise NotImplementedError
    
    @property
    def headers(self):
        """
        """ 
        raise NotImplementedError 
        

class TornadoHttpclientHeaderManager(HeaderBuilder):
    """
    """
    default_headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch",
        "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
        "Connection":"keep-alive",
        "Cookie":"",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36",         
    }    
    def add_cookie(self,cookie):
        """
            cookie实例：
            ['__cfduid=d91d42345b0e1eacce8110aa7a67e0b111458022618; expires=Wed, 15-Mar-17 06:16:58 GMT; path=/; domain=.wooyun.org; HttpOnly', 'PHPSESSID=i7sm27865ja25o0ba516vd9fi5; path=/']

        """
        self.default_headers["Cookie"] += ";".join(cookie)

    def update_cookie(self,cookie):
        self.default_headers["Cookie"] = ";".join(cookie)
    
    def alter_useragent(self,user_agent):
        self.default_headers["User-Agent"] = user_agent
    
    @property
    def headers(self):

        return HTTPHeaders(self.default_headers)
    
    @classmethod
    def config(cls,**kwargs):
        cls.default_headers = dict(cls.default_headers,**kwargs)
        
    def echo_headers(self,headers):
        print "*********************"
        for k,v in headers.get_all():
            print "%s :%s "% (k,v)
        print "<<<<<<<<<<<<<<<<<<<<<"        
        
class Response(object):
    """
    """
    
    def __init__(self,response):
        #self.response = response
        pass
        
    def xpath(self,selector):
        raise NotImplementedError
    
    def css(self,selector):
        raise NotImplementedError
    
    def build_dom(self,response_source):
        return lxml.html.document_fromstring(response_source)
        
    def dom_operation(self,operation,*args,**kwargs):
        if not hasattr(self,"dom"):
            raise AttributeError
        if hasattr(self.dom,operation):
            return getattr(self.dom,operation)(*args,**kwargs)
        else:
            raise AttributeError("DOM has no method or attribute like %s" % operation)
    
class TornadoResponse(Response):
    """
    """
    def __init__(self,response):
        self.response = response 
        self.dom =  self.build_dom(response.body)
        self.url = response.effective_url
        self.request_time = response.request_time
    
    def xpath(self,selector):
        return self.dom.xpath(selector)
    
    def css(self,selector):
        return self.dom.cssselector(select)
        
    #def dom_operation(self,operation,*args,**kwargs):
    #    if hasattr(self.dom):
    #        return getattr(self.dom,operation)(*args,**kwargs)
    #    else:
    #        raise AttributeError("DOM has no method or attribute like %s" % operation)
              