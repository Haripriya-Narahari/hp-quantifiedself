from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import *
from flask_caching import *


engine = create_engine("sqlite:///./database.sqlite3")
Session = scoped_session(sessionmaker(bind=engine))
engine = None
session = Session()
Base = declarative_base()
db = SQLAlchemy()
app = Flask(__name__)
with app.app_context():
    cache = Cache(app,config={'CACHE_TYPE': 'RedisCache'})
    cache.init_app(app)
