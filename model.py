from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean
from database import Base
from database import db
from flask_security import UserMixin,RoleMixin
from flask_login import LoginManager

class Login(db.Model, UserMixin):
    __tablename__ = 'login'
    username = Column(String,nullable=False, primary_key = True)
    password = Column(String,nullable=False)
    usertitle = Column(String,nullable=False)
    active = Column(Boolean,nullable=False)
    fs_uniquifier = Column(String,unique = True, nullable=False)
'''
class User(Base, UserMixin):
    __tablename__ = 'user'
    username = Column(String,nullable=False, primary_key = True)
    usertitle = Column(String,nullable=False)
    email = Column(String,nullable=False)
    password = Column(String,nullable=False)
    active = Column(String,nullable=False)
    fs_uniquifier = Column(String,unique = True, nullable=False)
'''
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    roleid = Column(Integer,nullable=False, primary_key = True,autoincrement=True)
    name = Column(String,nullable=False)
    description = Column(String,nullable=False)
'''
class RolesUsers(
'''
class Logger(db.Model):
    __tablename__ = 'logger'
    logid = Column(Integer,nullable=False, primary_key = True,autoincrement=True)
    trackid = Column(Integer,ForeignKey("tracker.trackid"))
    username = Column(Integer, ForeignKey("login.username"))
    when = Column(String, nullable=False)
    value = Column(String, nullable=False)
    notes = Column(String)

class Tracker(db.Model):
    __tablename__ = 'tracker'
    trackid = Column(Integer,nullable=False, primary_key = True,autoincrement=True)
    username = Column(String, ForeignKey("login.username"))
    trackername = Column(String, nullable=False)
    trackdesc = Column(String)
    trackdate = Column(String, nullable=False)
    tracktype= Column(String, nullable=False)

