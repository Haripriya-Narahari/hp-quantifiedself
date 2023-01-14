# Quantified Self - Multi user Tracking application

## Description:
To create an application that will allow multiple users to login, add their own trackers, log data for trackers, get customized summary report, daily reminders and insight on the summary of their logs.

The application is served using Python flask. API end points have been built using flask-restful. SQLite provides database support along with SQLAlchemy. VueJS, JavaScript framework has been used to fetch data from the api and render it to the client. Batch jobs and asynchronous tasks for sending monthly summary mails, daily reminders and triggering CSV export is implemented using Celery. Redis database has been used for enabling caching in the application

## Technologies Used:

Flask – Web support and APIs

SQLAlchemy – SQLite support

VueJS – User Interface

Celery – Batch Jobs

Redis – Caching

## DB Schema design:
### Tables used:
#### Login: To hold details of users

#### Tracker: To add details about the tracker

#### Logger: To hold details of log of trackers by various users.

## Architectures:

### Functions:
Landing_page(): Opens the start.html page for user login

Newuser(): Opens newuser.html page for user to add a new login when initiated

Dashboard(): Opens the dashboard.html for a particular user to list all trackers

Addtrack(): Opens the add tracker form for a particular user

Edittrack(): Opens edittracker.html with prepopulated values to edit and saves changes

Addlog(): Opens Logtracker.html to adds log when initiated

Editlog():Opens editlog.html with prepopulated values to edit and saves changes

Summary(): Opens the summary.html for a particular tracker to list all logs

### APIs and Resources:

UserLogin - "/api/newuser": Creates a newuser

UserInfo - "/api/<string:username>": Gets information of all the users

TrackerAdd - "/api/tracker/<string:username>/add": Creates a new tracker

TrackerUpdate - "/api/tracker/<int:trackid>/edit" : Edits a given tracker

TrackerDelete - "/api/tracker/<int:trackid>/delete" : Delete a specified tracker

TrackerInfo - "/api/tracker/<string:username>": Gets tracker information for a username

LogAdd, "/api/log/<int:trackid>/add" : Adds a log for a tracker

LogInfo, "/api/log/<int:trackid>" : Gets log information for a tracker

LogDelete, "/api/log/<int:logid>/delete" : Deletes a specified log

LogUpdate, "/api/log/<int:logid>/edit" : Edits a particular log

GenData, "/api/<int:trackid>/summary" :Gets Summary of the logs for a tracker

### Asynchronous and Scheduled Tasks

data_to_csv – Converts log/tracker details to csv when requested by the user

send_reminder – Sends daily reminders if the user has not logged on in mail

send_monthly_report – Sends monthly reports to users about the trackers through mail
