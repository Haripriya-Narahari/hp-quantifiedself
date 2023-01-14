#from cProfile import label
from flask_restful import Resource, Api, fields, marshal_with
from flask import redirect, jsonify, flash
from flask_restful import reqparse
from model import *
from validation import *
from database import db
from sqlalchemy import select,update,delete
from flask_security import auth_required, hash_password
#from flask_cors import *
import uuid
import matplotlib.pyplot as plt
import os
import io
import base64
from worker import celery
import pandas as pd
import task
from datetime import date
from database import cache

login_fields = { 'username' : fields.String,
    'password' : fields.String,
    'usertitle' : fields.String,
    'active' : fields.Integer,
    'fs_uniquifier' : fields.String,
}

login_parser = reqparse.RequestParser()
login_parser.add_argument('username')
login_parser.add_argument('password')
login_parser.add_argument('usertitle')
login_parser.add_argument('active')
login_parser.add_argument('fs_uniquifier')

tracker_fields = { 'trackid' : fields.Integer,
    'username' : fields.String,
    'trackername' : fields.String,
    'trackdesc' : fields.String,
    'trackdate' : fields.String,
    'tracktype' : fields.String,
}

tracker_parser = reqparse.RequestParser()
tracker_parser.add_argument('trackid')
tracker_parser.add_argument('username')
tracker_parser.add_argument('trackername')
tracker_parser.add_argument('trackdesc')
tracker_parser.add_argument('trackdate')
tracker_parser.add_argument('tracktype')


log_fields = { 'logid' : fields.Integer,
    'trackid' : fields.Integer,
    'username' : fields.String,
    'when' : fields.String,
    'value' : fields.String,
    'notes' : fields.String,
}

log_parser = reqparse.RequestParser()
log_parser.add_argument('logid')
log_parser.add_argument('trackid')
log_parser.add_argument('username')
log_parser.add_argument('when')
log_parser.add_argument('value')
log_parser.add_argument('notes')

class UserLogin(Resource):
    @marshal_with(login_fields)
    #@cross_origin(orgins="http://127.0.0.1:5000")
    def get(self):
        arg = login_parser.parse_args()
        username = arg.get("username",None)
        password = arg.get("password",None)
        print(username,password)
        if username is None:
            raise ValidationError(status_code=400,error_code='UE1001',error_message='Username is required')
        if password is None:
            raise ValidationError(status_code=400,error_code='UE1002',error_message='Password is required')
        log = db.session.query(Login).filter(Login.username == username).first()
        passwd = db.session.execute(select(Login.password).where(Login.username == username)).scalar()
        if passwd == password:
            return log
        else:
            return "ERROR", 400

    
    @marshal_with(login_fields)
    #@cross_origin(orgins="http://127.0.0.1:5000")
    def post(self):
        arg = login_parser.parse_args()
        username = arg.get("username",None)
        password = arg.get("password",None)
        usertitle = arg.get("usertitle",None)
        print(username,password,usertitle)
        if username is None:
            raise ValidationError(status_code=400,error_code='UE1001',error_message='Username is required')
        if password is None:
            raise ValidationError(status_code=400,error_code='UE1002',error_message='Password is required')
        user = db.session.query(Login).filter(Login.username == username).first()
        if user:
            raise ValidationError(status_code=400,error_code='UE1003',error_message='Username is used')
        uniq = uuid.uuid1().hex
        log = Login(username = username, password = hash_password(password), usertitle =usertitle, active=1, fs_uniquifier=uniq)
        print(log)
        db.session.add(log)
        db.session.commit()
        return "Success", 200


class UserInfo(Resource):
    @marshal_with(login_fields)
    #@cross_origin(orgins="http://127.0.0.1:5000")
    def get(self,username):
        @cache.cached(timeout=50)
        def get_login(username):
            log = db.session.query(Login).filter(Login.username == username).scalar()
            return log
        l = get_login(username)
        return l
    
class TrackerInfo(Resource):
    @marshal_with(tracker_fields)
    @auth_required("token")
    def get(self,username):
        @cache.cached(timeout=50)
        def get_tracker(username):
            log = db.session.query(Tracker).filter(Tracker.username == username).all()
            return log
        l = get_tracker(username)
        return l


class TrackerAdd(Resource):
    
    @marshal_with(tracker_fields)
    @auth_required("token")
    def post(self,username):
        cache.clear()
        arg = tracker_parser.parse_args()
        trackername = arg.get("trackername",None)
        trackdesc = arg.get("trackdesc",None)
        trackdate = arg.get("trackdate",None)
        tracktype = arg.get("tracktype",None)
        username = arg.get("username",None)
        print(trackername,trackdesc,trackdate,tracktype)
        if trackername is None:
            raise ValidationError(status_code=400,error_code='TE1001',error_message='Tracker name is required')
        if trackdesc is None:
            raise ValidationError(status_code=400,error_code='TE1002',error_message='Tracker description is required')
        log = Tracker(username = username, trackername=trackername, trackdesc = trackdesc, trackdate = trackdate, tracktype = tracktype)
        db.session.add(log)
        db.session.commit()
        return log
    
    @marshal_with(tracker_fields)
    @auth_required("token")
    def get(self,trackid):
        @cache.cached(timeout=50)
        def get_tracker(username):
            log = db.session.query(Tracker).filter(Tracker.username == username).all()
            return log
        l = get_tracker(username)
        return l

class TrackerUpdate(Resource):
    
    @marshal_with(tracker_fields)
    @auth_required("token")
    def get(self,trackid):
        @cache.cached(timeout=50)
        def get_tracker_i(trackid):
            log = db.session.query(Tracker).filter(Tracker.trackid == trackid).all()
            return log
        l = get_tracker_i(trackid)
        return l
  
    @marshal_with(tracker_fields)
    @auth_required("token")
    def post(self,trackid):
        cache.clear()
        arg = tracker_parser.parse_args()
        trackid = arg.get("trackid",None)
        trackername = arg.get("trackername",None)
        trackdesc = arg.get("trackdesc",None)
        trackdate = arg.get("trackdate",None)
        tracktype = arg.get("tracktype",None)
        if trackername is None:
            raise ValidationError(status_code=400,error_code='TE1001',error_message='Tracker name is required')
        if trackdesc is None:
            raise ValidationError(status_code=400,error_code='TE1002',error_message='Tracker description is required')
        s1 = db.session.execute(update(Tracker).where(Tracker.trackid == trackid).values(trackername=trackername))
        
        s2 = db.session.execute(update(Tracker).where(Tracker.trackid == trackid).values(trackdesc=trackdesc))
        #db.session.commit(s1)
        s3 = db.session.execute(update(Tracker).where(Tracker.trackid == trackid).values(tracktype=tracktype))
        s3 = db.session.execute(update(Tracker).where(Tracker.trackid == trackid).values(trackdate=trackdate))
        db.session.commit()
        log = db.session.query(Tracker).filter(Tracker.trackid == trackid).scalar()
        return log

    
class TrackerDelete(Resource):

    
    @marshal_with(tracker_fields)
    @auth_required("token")
    def get(self,trackid):
        @cache.cached(timeout=50)
        def get_tracker_i(trackid):
            log = db.session.query(Tracker).filter(Tracker.trackid == trackid).all()
            return log
        l = get_tracker_i(trackid)
        return l
    
    @auth_required("token")
    def post(self,trackid):
        cache.clear()
        arg = tracker_parser.parse_args()
        trackid = arg.get("trackid",None)
        db.session.execute(delete(Tracker).where(Tracker.trackid == trackid))
        db.session.commit()
        return "Deleted"

class LogAdd(Resource):
    
    @marshal_with(log_fields)
    @auth_required("token")
    def post(self,trackid):
        cache.clear()
        arg = log_parser.parse_args()
        trackid = arg.get("trackid",None)
        username = arg.get("username",None)
        when = arg.get("when",None)
        value = arg.get("value",None)
        notes = arg.get("notes",None)
        if when is None:
            raise ValidationError(status_code=400,error_code='LE1001',error_message='Date is required')
        if value is None:
            raise ValidationError(status_code=400,error_code='TE1002',error_message='Value is required')
        log = Logger(trackid = trackid, username = username, when = when, value = value, notes = notes)
        curr_date= date.today()
        db.session.add(log)
        s4 = db.session.execute(update(Tracker).where(Tracker.trackid == trackid).values(trackdate=curr_date))
        db.session.commit()
        return log

    @marshal_with(log_fields)
    @auth_required("token")
    def get(self,logid):
        @cache.cached(timeout=50)
        def get_tracker_i(logid):
            log = db.session.query(Logger).filter(Logger.logid == logid).all()
            return log
        l = get_tracker_i(logid)
        return l

class LogUpdate(Resource):
    
    @marshal_with(log_fields)
    @auth_required("token")
    def get(self,logid):
        @cache.cached(timeout=50)
        def get_tracker_i(logid):
            log = db.session.query(Logger).filter(Logger.logid == logid).all()
            return log
        l = get_tracker_i(logid)
        return l
        
    @marshal_with(log_fields)
    @auth_required("token")
    def post(self,logid):
        cache.clear()
        arg = log_parser.parse_args()
        when = arg.get("when",None)
        value = arg.get("value",None)
        notes = arg.get("notes",None)
        if when is None:
            raise ValidationError(status_code=400,error_code='LE1001',error_message='Date is required')
        if value is None:
            raise ValidationError(status_code=400,error_code='TE1002',error_message='Value is required')
        
        
        s1 = db.session.execute(update(Logger).where(Logger.logid == logid).values(when=when))
        s2 = db.session.execute(update(Logger).where(Logger.logid == logid).values(value=value))
        s3 = db.session.execute(update(Logger).where(Logger.logid == logid).values(notes=notes))
        curr_date= date.today()
        trackid = db.session.execute(select(Logger.trackid).where(Logger.logid == logid)).scalar()
        s4 = db.session.execute(update(Tracker).where(Tracker.trackid == trackid).values(trackdate=curr_date))
        db.session.commit()
        log = db.session.query(Logger).filter(Logger.logid == logid).scalar()
        return log

class LogInfo(Resource):
    
    @marshal_with(log_fields)
    @auth_required("token")
    def get(self,trackid):
        @cache.cached(timeout=50)
        def get_tracker_i(trackid):
            log = db.session.query(Logger).filter(Logger.trackid == trackid).all()
            return log
        l = get_tracker_i(trackid)
        return l

class LogDelete(Resource):
    
    @marshal_with(log_fields)
    @auth_required("token")
    def get(self,logid):
        @cache.cached(timeout=50)
        def get_tracker_i(logid):
            log = db.session.query(Logger).filter(Logger.logid == logid).all()
            return log
        l = get_tracker_i(logid)
        return l

    @auth_required("token")
    def post(self,logid):
        cache.clear()
        arg = log_parser.parse_args()
        logid = arg.get("logid",None)
        db.session.execute(delete(Logger).where(Logger.logid == logid))
        db.session.commit()
        return "Deleted"

class GenData(Resource):
    def gen_img(self,w,v):
        plt.plot(w,v,'g--')
        plt.xlabel('Date')
        plt.ylabel('Intensity')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.clf()
        img.seek(0)
        image_data = base64.b64encode(img.getvalue()).decode()
        plt.switch_backend('agg')
        return image_data

    def gen_img2(self,w,v):
        plt.bar(w, v,  color ='blue',width=0.1)
        plt.plot(w,v,'--',color='black')
        plt.xlabel('Date')
        plt.ylabel('TIme duration')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.clf()
        img.seek(0)
        image_data = base64.b64encode(img.getvalue()).decode()
        plt.switch_backend('agg')
        return image_data

    def gen_img3(self,w,v):
        x = 0.1
        y = 0.1
        color = ['red','blue','green']
        num = 0
        for i in range(len(v)):
            plt.text(x, y, v[i], bbox=dict(facecolor=color[num], alpha=0.7))
            x += 0.05
            y += 0.05
            num = (num+1)%3
        plt.xlabel('Date')
        plt.ylabel('Update')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.clf()
        img.seek(0)
        image_data = base64.b64encode(img.getvalue()).decode()
        plt.switch_backend('agg')
        return image_data

    @auth_required("token")
    def get(self,trackid):
        when = db.session.execute(select(Logger.when).where(Logger.trackid == trackid)).all()
        value = db.session.execute(select(Logger.value).where(Logger.trackid == trackid)).all()
        w = []
        v = []
        for i in when:
            w.append(i[0])
        rtype = db.session.execute(select(Tracker.tracktype).where(Tracker.trackid == trackid)).scalar()
        if rtype=='Numerical' or rtype=='Numeric':
            for i in value:
                try:
                    v.append(int(i[0]))
                except:
                    v.append(0)
            image_data = self.gen_img(w,v)
        elif rtype=='Time':
            for i in value:
                if i[0] == 'Less than 30 mins':
                    v.append(0.5)
                elif i[0] == '1 - 3 hours':
                    v.append(2)
                elif i[0] == '3 - 5 hours':
                    v.append(4.5)
                else:
                    v.append(6)
            image_data = self.gen_img2(w,v)
        elif rtype=='Text' or rtype[0:3]=='MCQ':
            for i in value:
                v.append(i[0])
            image_data = self.gen_img3(w,v)
        return image_data

class ConvertTrackCSV(Resource):
    @auth_required("token")
    def get(self,username):
        logo = db.session.query(Tracker).filter(Tracker.username == username).all()
        log = []
        for l in logo:
            log.append(l.__dict__)
        for l in log:
            l['_sa_instance_state'] = ""
            del l['_sa_instance_state']
        print(log)
        job = task.data_to_csv.apply_async(args=(log,username,))
        res = job.wait()
        return str(res) , 200

class ConvertLogCSV(Resource):
    @auth_required("token")
    def get(self,trackid):
        logo = db.session.query(Logger).filter(Logger.trackid == trackid).all()
        log = []
        for l in logo:
            log.append(l.__dict__)
        for l in log:
            l['_sa_instance_state'] = ""
            del l['_sa_instance_state']
        job = task.data_to_csv.apply_async(args=(log,trackid,))
        res = job.wait()
        return str(res) , 200