from email.mime.multipart import MIMEMultipart
import smtplib
from worker import celery
from database import db, Session
from model import *
from validation import *
from database import db
from sqlalchemy import select,update,delete
import pandas as pd
from celery.schedules import crontab
from datetime import date
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
import smtplib
from email.mime.text import *
from email.mime.multipart import *
from email.mime.base import *
from jinja2 import *
from email import encoders
from weasyprint import HTML
import matplotlib.pyplot as plt
import os
import io
import base64

curr_date= date.today()

@celery.task
def data_to_csv(log,name):
    df = pd.DataFrame(data=log) 
    df.to_csv(str(name)+'.csv')
    return "Success"

@celery.task
def send_reminder():
    log = []
    engine = create_engine("sqlite:///./database.sqlite3")
    Session = scoped_session(sessionmaker(bind=engine))
    engine = None
    session = Session()
    Base = declarative_base()
    db = SQLAlchemy()
    logo = session.query(Tracker).filter(Tracker.trackdate==curr_date).all()
    
    for l in logo:
        log.append(l.__dict__)
    name_log = []
    for l in log:
        name_log.append(l['username'])
    unames = session.query(Login.username,Login.usertitle).all()
    l3 = [x[1] for x in unames if x[0] not in name_log]
    for email in l3:
        msg = MIMEMultipart()
        if email.__contains__('@') : 
            msg["From"] = "haripriyanarahari28@gmail.com"
            msg["To"] = email
            msg["Subject"] = "Daily Reminders"

            msg.attach(MIMEText("<h4>Hi!!</h4> <br>We find you have not logged in your tracker today, Please log your tracker <br> <br> Reagrds,<br>The GetTrackingTeam","html"))
            s = smtplib.SMTP(host="localhost",port=1025)
            s.login("hpn286@hpn.com","")
            s.send_message(msg)
            s.quit()
        
    return "Success"

@celery.task
def send_monthly_report():
    def gen_img(w,v):
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

    def gen_img2(w,v):
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

    def gen_img3(w,v):
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
    engine = create_engine("sqlite:///./database.sqlite3")
    Session = scoped_session(sessionmaker(bind=engine))
    engine = None
    session = Session()
    unames = session.query(Login.username).all()
    logo = []
    logg = []
    va = []
    with open("templates/report_html.html") as file:
        templ = Template(file.read())
        for name in unames:
            image_data = []
            logo = session.query(Tracker.trackid,Tracker.trackdate,Tracker.trackdesc,Tracker.trackername,Tracker.tracktype).filter(Tracker.username==name[0]).all()
            logg = session.query(Logger.username,Logger.trackid,Logger.logid,Logger.notes,Logger.value,Logger.when).filter(Logger.username==name[0]).all()
            data = {}
            for l in logo:
                data[l[3]] = []
                for lo in logg:
                    if lo[1] == l[0]:
                        data[l[3]].append(list(lo))
            unames = session.query(Login.username,Login.usertitle).all()
            l3 = [x[1] for x in unames]
            for l in logo:
                if type(l) == Tracker:
                    logo.remove(l)
            
                when = session.execute(select(Logger.when).where(Logger.trackid == l["trackid"])).all()
                value = session.execute(select(Logger.value).where(Logger.trackid == l["trackid"])).all()
                w = []
                v = []
                for i in when:
                    w.append(i[0])
                rtype = session.execute(select(Tracker.tracktype).where(Tracker.trackid == l["trackid"])).scalar()
                if rtype=='Numerical' or rtype=='Numeric':
                    for i in value:
                        try:
                            v.append(int(i[0]))
                        except:
                            v.append(0)
                    image_data.append(gen_img(w,v))
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
                    image_data.append(gen_img2(w,v))
                elif rtype=='Text' or rtype[0:3]=='MCQ':
                    for i in value:
                        v.append(i[0])
                    image_data.append(gen_img3(w,v))
            val = []
            for d in data:
                for n in data[d]:
                    val.append(list(n))
            va.append(val)
            stri = templ.render(name = name[0],data=data,log=logg,img=image_data,val = va)
            html = HTML(string=stri)
            file = str(name[0])+".pdf"
            html.write_pdf(target=file)
            msg = MIMEMultipart()
            for email in l3:
                if email.__contains__('@') : 
                    msg["From"] = "haripriyanarahari28@gmail.com"
                    msg["To"] = email
                    msg["Subject"] = "Monthly Progress"
                    msg.attach(MIMEText("Hi!! \n Its a new month, we have brought you your monthly report!! \n Reagrds, \n GetTracking Team","plain"))
                    at = open(file, "rb")
                    pay = MIMEBase('application', 'octet-stream')
                    pay.set_payload((at).read())
                    encoders.encode_base64(pay)

                    pay.add_header('Content-Disposition', "attachment; filename= %s" % file)
                    msg.attach(pay)
                    s = smtplib.SMTP(host="localhost",port=1025)
                    s.login("hpn286@hpn.com","")
                    s.send_message(msg)
                    s.quit()
            logs = []
            logo = []

    return "Success"

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=14, minute=0),
        send_reminder.s(),
    )

    sender.add_periodic_task(
        crontab(0, 0, day_of_month='1'),
        send_monthly_report.s(),
    )

