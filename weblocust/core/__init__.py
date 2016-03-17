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
        
    
class SigleInstance(type):
	"""
		实现单列模式的元类
		总之，metaclass的主要任务是：
		拦截类，
		修改类，
		返回类
	"""
	
	def __init__(cls,classname,parrentstuple,attrdict):
		"""
			这个构造函数应该是创建 SigleInstance本身
			每次再给一个类加上metalcass属性时：这个元类就被创建一次
			__init__只是初始化，不会返回值
			__init__虽然是初始化 SigleInstance 实例，但是任何在这个函数中的属性都会被赋给被创建的类（类变量)
		"""
		super(SigleInstance,cls).__init__(classname,parrentstuple,attrdict)
		cls.instance = None
		
	
	
	def __call__(cls,*args,**kargs):
		"""
			这个实例方法才是去创建对象
			就好像现在才实现 type(classname,superclass,dict)一样
			创建对象的时候直接调用singleinstance()这个方法实现创建对象
		"""
		if cls.instance:
			return cls.instance
		else:
			cls.instance = super(SigleInstance,cls).__call__(*args,**kargs)
			return cls.instance        
    