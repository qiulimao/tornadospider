#coding:utf-8
from weblocust import settings

class NodeSettings(object):
    
    @classmethod
    def configure(cls,**kwargs):
        for k,v in kwargs.items():
            if hasattr(settings,k.upper()):
                setattr(settings,k.upper(),v)
