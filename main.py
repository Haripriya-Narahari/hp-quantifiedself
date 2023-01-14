from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy import func
import os
from database import db
from flask_security import Security, SQLAlchemySessionUserDatastore, auth_required, hash_password
#from database import db
from flask_session import Session
from model import Tracker,Logger,Login,Role
import worker
from flask_restful import Resource, Api
from config import DevelopmentConfig
from flask_cors import CORS
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_caching import Cache
app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
engine = create_engine("sqlite:///./database.sqlite3")
db.init_app(app)
api = Api(app)
cache = Cache(app)
cache.init_app(app)
#app.app_context().push()
#session = Session()

user_datastore = SQLAlchemySessionUserDatastore(db.session, Login, Role)
CORS(app,  supports_credentials=True, resources={r"/*": {"origins": "*"}})

from api import *
api.add_resource(UserLogin, "/api/newuser")
api.add_resource(UserInfo, "/api/<string:username>")
api.add_resource(TrackerAdd, "/api/tracker/<string:username>/add" )
api.add_resource(TrackerUpdate, "/api/tracker/<int:trackid>/edit" )
api.add_resource(TrackerDelete, "/api/tracker/<int:trackid>/delete" )
api.add_resource(TrackerInfo, "/api/tracker/<string:username>")
api.add_resource(LogAdd, "/api/log/<int:trackid>/add")
api.add_resource(LogInfo, "/api/log/<int:trackid>")
api.add_resource(LogDelete, "/api/log/<int:logid>/delete")
api.add_resource(LogUpdate, "/api/log/<int:logid>/edit")
api.add_resource(GenData, "/api/<int:trackid>/summary")
api.add_resource(ConvertTrackCSV, "/api/tracker/csv/<string:username>")
api.add_resource(ConvertLogCSV, "/api/log/csv/<int:trackid>")
celery = worker.celery
celery.conf.update(
            broker_url = app.config["CELERY_BROKER_URL"],
            result_backend = app.config["CELERY_RESULT_BACKEND"]
        )

if __name__ == '__main__':
    
    security = Security(app, user_datastore)
    
    api.init_app(app)
    #app.app_context().push()
    
    app.app_context().push()
    with app.app_context():
        from controllers import *
        db.create_all()
        celery.Task = worker.ContextTask
        cache.init_app(app)
        app.run()
        
        
        
