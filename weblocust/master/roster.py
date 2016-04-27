#coding:utf-8
##
# roster
##
from weblocust.master.table import session,SqliteTable
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime,timedelta
from weblocust import settings

__all__ = ["RedisRoster","SqliteRoster"]

class RosterBackend(object):
    """
        interface of Roster.
    """
    @classmethod
    def addslave(cls,ip,port,status):
        """ add a slave to the roster """
        raise NotImplementedError

    @classmethod
    def removeslave(cls,ip,port):
        """ remove a slave from the roster """
        raise NotImplementedError

    @classmethod
    def updatestatus(cls,ip,port,status):
        """ update a slave in the roster """
        raise NotImplementedError

    @classmethod
    def update_or_add(cls,ip,port,status):
        """ update or add a slave;
            if slave exists update it 
            else create a new slave 
        """
        raise NotImplementedError

    @classmethod
    def remove_zoobies(cls):
        """ remove slaves that are not alive """
        raise NotImplementedError


class RedisRoster(RosterBackend):
    """
        redis that stores slave status
    """
    pass

class SqliteRoster(RosterBackend):
    """
        sqlite that sotres slave status
    """

    @classmethod
    def slave_add(cls,ip,port,status):
        new_slave = SqliteTable(ip=ip,port=port,**status)
        session.add(new_slave)
        session.commit()

    @classmethod
    def slave_remove(cls,ip,port):
        session.query(SqliteTable).filter(SqliteTable.ip==ip,SqliteTable.port==port).delete()
        session.commit()

    @classmethod
    def slave_update(cls,ip,port,status):
        session.query(SqliteTable).filter(SqliteTable.ip==ip,SqliteTable.port==port).update(status)
        session.commit()

    @classmethod
    def update_or_add(cls,ip,port,status):
        try:
            slave = session.query(SqliteTable).filter(SqliteTable.ip==ip,SqliteTable.port==port).one()
            cls.slave_update(ip,port,status)
        except NoResultFound:
            cls.slave_add(ip,port,status)

    @classmethod
    def remove_zombies(cls):
        """ remove slave zombies ,this method can be called peroidly,but not frequently,
        because it is operating the database
        """
        current_time = datetime.now()
        valide_period = timedelta(seconds=settings.DETECT_ZOMBIE_FRENQUENCY)
        expire = current_time - valide_period
        zombie_slaves = session.query(SqliteTable).filter(SqliteTable.update_time < expire).delete()
        print zombie_slaves

    @classmethod
    def all(cls,offset=0,limit=100):
        """ get all the slaves """
        all_slaves = session.query(SqliteTable).offset(offset).limit(limit).all()
        return all_slaves


