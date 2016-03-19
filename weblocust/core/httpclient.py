#coding:utf-8
from . import SigleInstance
from tornado.httputil import HTTPHeaders
from tornado.httpclient import HTTPRequest
from lxml import etree
from w3lib.encoding import html_to_unicode, resolve_encoding,html_body_declared_encoding, http_content_type_encoding
import urlparse
import cookielib

class WebLocustRequest(object):
    def __init__(self,url,callback):
        self.url = url
        self.callback = callback

#class Headers(HTTPHeaders):
#    """
#        in order to user CookieJar,
#        implement the header instance with getallmatchingheaders(name) method
#    """
#    def getallmatchingheaders(self,name):
#        return self.get_list(name)


class Request(object):
    """
    """
    DEFAULT_USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36"
    
    def __init__(self,url,data=None,cookie=None,user_agent=None,callback=None,**kwargs):
        """
            parameter:
                url:        an url to request 
                data:       if data is set , the request automacticlly turn into a POST request;default is GET
                cookie:     the cookie to be send to the server
                            the cookie style is like this:['a=b,c=d','iu=19'] or 
                        
                            PHPSESSID=web5~cbqhkbt3vhrmh5oseuj6cabgt0; 
                            Hm_lvt_e23800c454aa573c0ccb16b52665ac26=1456994167,1457403113,1458138303,1458355484; 
                            Hm_lpvt_e23800c454aa573c0ccb16b52665ac26=1458355484; _ga=GA1.2.1640863779.1455850547
                            
                user_agent: the user_agent,you can change it on every request 
                callback  : callback of the request 
        """
        self.url = url
        self.data = None
        self.method = "POST" if data else "GET"
        self.user_agent = user_agent if user_agent else self.DEFAULT_USERAGENT
        self.callback = callback
        self.cookie = cookie
        for k,v in kwargs.items():
            setattr(self,k,v) 
            
    def get_full_url(self):
        return self.url
    
    def get_host(self):
        """ find the server hostname """
        return urlparse.urlparse(self.url).hostname
        
    def unverifiable(self):
        return False 
    
    def is_unverifiable():
        return self.unverifiable() 
    
    def get_origin_request_host(self):
        self.get_host()
        
        

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

class Build2TornadoRequest(object):

    @classmethod
    def build_request(cls,request,response=None):
        """
            if request is added , request will be built with cookie enabled 
        """
        default_headers_info = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, sdch",
                "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
                "Connection":"keep-alive",
                "Cookie":None,
                "User-Agent":request.user_agent,       
            }
            
        if response:
            cookie_jar = cookielib.CookieJar(policy=cookielib.DefaultCookiePolicy())
            cookies = cookie_jar.make_cookies(response,request)
            print "the cookies is type of [%s]" % type(cookies)
            default_headers_info["Cookie"] = ";".join(cookies) 
                    
        headers =  HTTPHeaders(default_headers_info)
        
        return HTTPRequest(request.url,headers=headers,follow_redirects=True,max_redirects=5,request_timeout=3)

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


#######################################
# the below code belongs to response  #
#######################################
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
    
          
    def info(self):
        """
            In order to use CookieJar,we must implement the method 
            
            returns an object with a getallmatchingheaders() method (usually a mimetools.Message instance).
            def getallmatchingheaders(self,name):
                Return a list of lines consisting of all headers matching name,if any. 
                Each physical line, whether it is a continuation line or not, is a separate list item. 
                Return the empty list if no header matches name.
                
            tornado_response.headers
        """
        
        headers = self.headers
        
        def getallmatchingheaders(self,name):
            return self.get_list(name)
        settattr(headers,getallmatchingheaders)
        
        return headers

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
        cookie = ";".join(tornado_response.headers.get_list("Set-Cookie"))
        headers = tornado_response.headers 
        ## cookie的样子：
        # ['a=b,c=2','d=123,d=232']
        ##            
        return Response(url,dom,rtt=rtt,code = code,cookie=cookie,headers=headers)
        
        
              