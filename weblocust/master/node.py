#coding:utf-8
from weblocust.master.roster import SqliteRoster

class Slave(object):
    """
        a slave object
    """

    roster = SqliteRoster 

    def __init__(self,ip,port):
        self.ip = ip
        self.port = port

    def _get_command(self):
        cmd = self.roster.get_command(self.ip,self.port)
        return cmd

    def greeting(self,status):
        """ greeting to the server """
        self.roster.update_or_add(self.ip,self.port,status)
        return self._get_command()

        #raise NotImplementedError

    def register(self,status):
        """ register the slave to backend """
        #raise NotImplementedError
        self.roster.slave_add(self.ip,self.port,status)

    def update(self,status):
        """ update slave's status """
        #raise NotImplementedError
        self.roster.slave_update(self.ip,self.port,status)

    def delete(self):
        """ delete slave's status """
        #raise NotImplementedError
        self.roster.slave_delete(self.ip,self.port)

    def start(self):
        """start the slave """
        #print "------------"
        status = {
            "cmd_running":True,
        }
        self.roster.slave_update(self.ip,self.port,status)

    def stop(self):
        """ stop the slave.but no kill the slave,just hold the slave """
        #raise NotImplementedError
        status = {
            "cmd_running":False,
        }
        self.roster.slave_update(self.ip,self.port,status)

    def pause(self):
        """ pasuse the slave """
        status = {
            "cmd_working":False,
        }
        self.roster.slave_update(self.ip,self.port,status)

    def resume(self):
        status = {
            "cmd_working":True,
        }
        self.roster.slave_update(self.ip,self.port,status)

    def exists(self):
        return self.roster.exists(self.ip,self.port)

    @classmethod 
    def set_roster(cls,roster):
        """ set the roster backend """
        cls.roster = roster

    @classmethod
    def remove_zombies(cls):
        cls.roster.remove_zombies()

    @classmethod
    def all(cls):
        return cls.roster.all()
