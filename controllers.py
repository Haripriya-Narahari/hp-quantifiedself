from urllib import response
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from requests import get,post,patch,delete
from flask import current_app as app
from model import *
from api import *
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask_security import login_required, hash_password, auth_required  
from flask_cors import *
from database import db
import uuid
from main import cache


engine = create_engine("sqlite:///./database.sqlite3")

@cross_origin(orgins="http://127.0.0.1:5000")
@app.route('/')
@cache.cached(timeout=50)
def landing_page():
    if request.method == 'GET':
        return render_template('home.html')
        
@cross_origin(orgins="http://127.0.0.1:5000")
@app.route('/login_user', methods = ['POST','GET'])
@cache.cached(timeout=50)
def login():
    return render_template('login_user.html')
       
@cross_origin(orgins="http://127.0.0.1:5000")
@app.route('/newuser', methods = ['POST','GET'])
@cache.cached(timeout=50)
def newuser():
    return render_template("newuser.html")
 
@app.route('/tracker/<string:username>/add', methods = ['POST','GET'])
@auth_required("token") 
@cache.cached(timeout=50)
def addtrack(username):
    return render_template('addtracker.html')

@auth_required("token")
@app.route('/tracker/<string:username>/<int:trackid>/edit', methods = ['POST','GET'])
def edittrack(username,trackid):
    return render_template('edittracker.html')


@cross_origin(orgins="http://127.0.0.1:5000")   
@app.route('/dashboard/<string:username>/', methods = ['POST','GET'])
@auth_required("token")
@cache.cached(timeout=50)
def dashboard(username):
    return render_template("dashboard.html")

@cross_origin(orgins="http://127.0.0.1:5000")   
@app.route('/tracker/<string:username>/<int:trackid>', methods = ['POST','GET'])
@auth_required("token")
@cache.cached(timeout=50)
def summary(username,trackid):
    return render_template('summary.html')

@cross_origin(orgins="http://127.0.0.1:5000")
@app.route('/log/<int:trackid>/add', methods = ['POST','GET'])
@auth_required("token")
@cache.cached(timeout=50)
def addlog(trackid):
    return render_template('logtracker.html')

@cross_origin(orgins="http://127.0.0.1:5000")
@app.route('/log/<int:logid>/edit', methods = ['POST','GET'])
@auth_required("token")
def editlog(logid):
    return render_template('editlog.html')

