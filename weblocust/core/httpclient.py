#coding:utf-8
#from . import SigleInstance
from tornado.httputil import HTTPHeaders
from tornado.httpclient import HTTPRequest
from lxml import etree
from w3lib.encoding import html_to_unicode, resolve_encoding,html_body_declared_encoding, http_content_type_encoding
import urlparse
import cookielib
import urllib




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
            

              

class RequestBuilder(object):
    """
        request 构造的接口类
        这个类的职责是：将weblocust当中的requet类，转换为其他框架当中的request
    """
    #__metaclass__ = SigleInstance
    
    @classmethod
    def build_request(cls,request):
        """
            返回一个request对象
        """
        raise NotImplementedError

class Build2TornadoRequest(RequestBuilder):
    """
        将请求构造为一个tornado的请求
    """
    @classmethod
    def build_request(cls,request):
        """
            keep it's duty simple
        """
        default_headers_info = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, sdch",
                "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
                "Connection":"keep-alive",
                "Cookie":request.cookie,
                "User-Agent":request.user_agent,       
            }           
                    
        headers =  HTTPHeaders(default_headers_info)
       
        post_data = urllib.urlencoding(request.data) if request.data else None
  
        return HTTPRequest(request.url,
                            method=request.method,
                            headers=headers,
                            body = post_data,
                            follow_redirects=True,
                            max_redirects=5,
                            request_timeout=3)


                   


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
            xpath 当中的黑科技：
            contains是一个字符串查找函数
            　　语法是：fn:contains(string1,string2)，
                表示如果 string1 包含 string2，则返回 true，否则返回 false。
            　　例如：contains('XML','XM')，结果：true。
             
            match是一个匹配正则表达式的函数
            　　语法是：fn:matches(string,pattern)，
                表示如果 string 参数匹配指定的模式，则返回 true，否则返回 false。
            　　例如：matches("12", "[0-9]{1,2}"), 结果：true。
            
            starts-with是一个字符串查找函数
            　　语法是：fn:starts-with(string,pattern)，
                表示如果 string 参数匹配指定的模式，则返回 true，否则返回 false。        
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
        except ValueError:
            dom = etree.fromstring(page_source)
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
        return Response(url,dom,rtt=rtt,code = code,cookie=cookie,headers=headers)
        
        
              