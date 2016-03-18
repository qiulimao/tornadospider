#coding:utf-8
from . import SigleInstance
from tornado.httputil import HTTPHeaders
from tornado.httpclient import HTTPRequest
from lxml import etree
from w3lib.encoding import html_to_unicode, resolve_encoding,html_body_declared_encoding, http_content_type_encoding
import urlparse


class WebLocustRequest(object):
    def __init__(self,url,callback):
        self.url = url
        self.callback = callback

class Request(object):
    """
    """
    DEFAULT_USERAGENT = "WebLocust(0.1)"
    
    def __init__(self,url,cookie=None,user_agent=None,callback=None,**kwargs):
        self.url = url
        self.user_agent = user_agent if user_agent else self.DEFAULT_USERAGENT
        self.callback = callback
        self.cookie = cookie
        for k,v in kwargs.items():
            setattr(self,k,v) 
        
        

class RequestBuilder(object):
    """
        request 构造的接口类
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
        tornado request 创造者
    """
    @classmethod
    def build_request(cls,url,headers):
        return HTTPRequest(url,headers=headers,follow_redirects=True,max_redirects=5,request_timeout=2)
            

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
            [
                '__cfduid=d91d42345b0e1eacce8110aa7a67e0b111458022618; expires=Wed, 15-Mar-17 06:16:58 GMT; path=/; domain=.wooyun.org; HttpOnly',
                'PHPSESSID=i7sm27865ja25o0ba516vd9fi5; path=/'
             ]

        """
        self.default_headers["Cookie"] += ";".join(cookie)

    def update_cookie(self,cookie):
        self.default_headers["Cookie"] = ";".join(cookie)
    
    def alter_useragent(self,user_agent):
        self.default_headers["User-Agent"] = user_agent
    
    @property
    def headers(self):
        
        header =  HTTPHeaders(self.default_headers)
        #self.echo_headers(header)
        return header
    
    @classmethod
    def config(cls,**kwargs):
        cls.default_headers = dict(cls.default_headers,**kwargs)
        
    def echo_headers(self,headers):
        print "*********************"
        for k,v in headers.get_all():
            print "%s :%s "% (k,v)
        print "<<<<<<<<<<<<<<<<<<<<<"        


##
# the below code belongs to response 
##
class Response(object):
    """
        weblocust当中统一的 response类
    """
    def __init__(self,url,dom,**kwargs):
        self.dom = dom
        self.url = url
        for k,v in kwargs.items():
            setattr(self,k,v)
            
    def xpath(self,query):
        """
        """
        return self.dom.xpath(query)
    
    def css(self,query):
        return self.dom.cssselector(query)
    
    def urljoin(self,link):
        return urlparse.urljoin(self.url,link)
        
    def dom_operation(self,operation,*args,**kwargs):
        """
        """
        if not hasattr(self,"dom"):
            raise AttributeError
        if hasattr(self.dom,operation):
            return getattr(self.dom,operation)(*args,**kwargs)
        else:
            raise AttributeError("DOM has no method or attribute like %s" % operation)

class ResponseBuilder(object):
    """
        response builder 接口
    """
    @classmethod
    def build_response(cls,*args,**kwargs):
        raise NotImplementedError
        

class TornadoResponseBuilder(ResponseBuilder):
    """
        根据tornado返回的response，创建weblocust当中的response
    """
    @classmethod
    def _headers_encoding(cls,response):
        """
            根据content-type查看编码类型
        """
        content_type = response.headers.get('Content-Type')
        return http_content_type_encoding(content_type)  
        
    @classmethod
    def _body_declared_encoding(cls,response):
        """
            根据body 查看编码类型。
            自动探测编码 是从scrapy学来的
        """
        return html_body_declared_encoding(response.body)
        
    @classmethod    
    def _detect_encoding(cls,response):
        """
          首先检测头部，其次是body，如果都没有编码信息，那就瞎猫当死耗子医，直接上utf-8
          错了让他返回一个空白提示页面       
        """
        return cls._headers_encoding(response) or cls._body_declared_encoding(response) or "utf-8"    
    
    @classmethod   
    def _build_dom(cls,response):
        """
            生成dom文档
        """
        page_encoding = cls._detect_encoding(response)
        page_source = response.body
        try:
            dom = etree.HTML(page_source.decode(page_encoding,'ignore'))
        except UnicodeDecodeError as e:            
            dom = etree.HTML("<html><head><title>NotAValidHTMLPage</title></head></html>".decode("utf-8"))
        return dom         
        
    @classmethod        
    def build_response(cls,tornado_response):
        
        url = tornado_response.effective_url
        dom = cls._build_dom(tornado_response)
        rtt = tornado_response.request_time  
        code = tornado_response.code
        cookie = ";".join(tornado_response.header.get_list("Set-Cookie"))
        ## cookie的样子：
        # ['a=b,c=2','d=123,d=232']
        ##            
        return Response(url,dom,rtt=rtt,code = code,cookie=cookie)
        
        
              