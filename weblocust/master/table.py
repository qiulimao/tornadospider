#!/usr/bin/env python
#coding:utf-8
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,Text,DateTime,Date,Enum,Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import os
from  datetime import datetime 
from sqlalchemy.orm.exc import NoResultFound

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASEURL = "sqlite:////%s"%os.path.join(CURRENT_DIR,"SlaveRoster.sqlite3")

engine = create_engine(DATABASEURL,echo=False)

Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()

class SqliteTable(Base):
    """
        persist slave status,
        we need to create union index (ip,port)
    """
    __tablename__ = "slave_status"

    id=Column(Integer,primary_key=True)
    ip = Column(String(32))
    port = Column(Integer)
    init_time = Column(DateTime,default=datetime.now)
    update_time = Column(DateTime,default=datetime.now,onupdate=datetime.now)

    role = Column(Enum("master","slave"),default="slave")
    state_running = Column(Boolean,default=0)
    state_working = Column(Boolean,default=0)
    state_workload = Column(Integer,default=0)
    state_qsize   = Column(Integer,default=0)

    cmd_running = Column(Boolean,default=0)
    cmd_working = Column(Boolean,default=0)





if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)