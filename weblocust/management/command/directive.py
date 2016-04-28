#coding:utf-8

from optparse import OptionGroup
from weblocust.management.webui.httpserver import tornadoweb
from weblocust import settings

class WebLocustCommand(object):
    """
        terminal command
    """
    controller_name="router"
    @classmethod
    def add_options(cls,parser):
        """
            add command options here 
        """
        parser.add_option("-c",'--controller',default="master",help="do a specific action",dest="controller",metavar="String")

        
    def run_command(self,options,*args):
        """
            Entry point for running commands
        """
        raise NotImplementedError



class RunMaster(WebLocustCommand):
    """
        this command run the project
    """
    controller_name="master"

    @classmethod
    def add_options(cls,parser):
        """
            this command can configure port option,
            default is 9999
        """
        group = OptionGroup(parser, "Controller:<master> options") 
        group.add_option('-p','--port',dest="port",default=9999,type="int",metavar="Integer",help="http server port,default is 9999")
        parser.add_option_group(group)    
        
    def run_command(self,options,*args):
        """
        """
        print "run master server on port %d ..."%options.port
        tornadoweb(options.port)

class RunSlave(WebLocustCommand):
    """
    """
    controller_name="slave"

    @classmethod
    def add_options(cls,parser):
        group = OptionGroup(parser,"Controller:<slave> options")
        group.add_option('-w',"--worker",dest="port",default=settings.CONCURRENCY,type="int",metavar="Integer",help="concurrency")

    def run_command(self,options,*args):
        """ """
        print "start worker now...."
