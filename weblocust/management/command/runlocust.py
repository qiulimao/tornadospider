#coding:utf-8
from weblocust.management.command import WebLocustCommand
from optparse import OptionGroup
from weblocust.management.webui.httpserver import tornadoweb

class RunLocust(WebLocustCommand):
    """
        this command run the project
    """
    
    @classmethod
    def add_options(cls,parser):
        """
            this command can configure port option,
            default is 9999
        """
        group = OptionGroup(parser, "Controller:RunLocust options") 
        group.add_option('-p','--port',dest="port",default=9999,type="int",metavar="Integer",help="http server port,default is 9999")
        parser.add_option_group(group)    
        
    def run_command(self,options,*args):
        """
            run the command ,this will be implement later
        """
        print "run the server on port %d"%options.port
        tornadoweb(options.port)
