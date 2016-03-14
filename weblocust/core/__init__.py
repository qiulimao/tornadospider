#coding:utf-8
from tornado import gen

def timer(interval=6,lifespan=60):
    def _wrapper(func):
        #调用定时任务的函数也必须是一个 coroutine
        @gen.coroutine 
        def __nostop_call(*args,**kwargs):
            lifetime = 0
            while lifetime < lifespan:
                lifetime += interval
                nxt = gen.sleep(interval)
                # 定时任务必须是 coroutine 
                # 所以被timer装饰的函数也必须是 coroutine
                yield func(*args,**kwargs)
                yield nxt            
        return __nostop_call
    return _wrapper
    

def crontab(func,interval=6,lifespan=60,func_args=[],func_kwargs={}):
    """
        定时器，和timer功能一样
        两种情况用于不同的场合
    """
    @gen.coroutine
    def _wrapper():
        lifetime = 0
        while lifetime < lifespan:
            lifetime += interval
            nxt = gen.sleep(interval)
            yield func(*func_args,**func_kwargs)
            yield nxt
    return _wrapper
        
    
        
    