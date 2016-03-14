#coding:utf-8

from optparse import OptionGroup
class WebLocustCommand(object):
    """
        terminal command
    """        
    @classmethod
    def add_options(cls,parser):
        """
            add command options here 
        """
        parser.add_option("-c",'--controller',default="RunLocust",help="do a specific action",dest="controller",metavar="String")

        
       
    
    def run_command(self,options,*args):
        """
            Entry point for running commands
        """
        raise NotImplementedError