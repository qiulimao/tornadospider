#coding:utf-8
import inspect
from importlib import import_module
from pkgutil import iter_modules
from weblocust.management.command import WebLocustCommand
from optparse import OptionParser

def walk_modules(path):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('scrapy.utils')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods

def iter_command_classes(module_name):
    """ 
    TODO: add `name` attribute to commands and and merge this function with
    # scrapy.utils.spider.iter_spider_classes
    """
    for module in walk_modules(module_name):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and \
               issubclass(obj,WebLocustCommand) and \
               obj.__module__ == module.__name__:
                yield obj     
                
def manage_command():
    """
        处理命令
    """
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage,version="%prog 0.1")
    _cmds = []
    for mod in iter_command_classes("weblocust.management.command"):
        mod.add_options(parser)
        _cmds.append(mod)
        
    
    options,args = parser.parse_args()
    
    cmd = filter(lambda x:True if x.__name__==options.controller else False,_cmds)
    if len(cmd) == 1:
        handler = cmd[0]()
        handler.run_command(options,*args)
    else:
        parser.error("no such command,run `weblocust --help` to get more detail")