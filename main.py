from flask import Flask, request, session, redirect, url_for
import urllib

import requests
from flask import Flask, render_template, abort
from calendar import Calendar
from datetime import date
import os
from flask import Flask, render_template_string
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter, LoginManager
from flask_login import login_user
import flask_login
from datetime import datetime, timedelta
import json
import time


# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vacation.sqlite')
    CSRF_ENABLED = True

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"MyApp" <noreply@example.com>')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))

    # Flask-User settings
    USER_APP_NAME = "AppName"  # Used by email templates

app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')
# app.secret_key = '72kErLTlV5R9z298cMOstnjN'

db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy

# Define the User data model. Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), server_default='')
    # User email information
    email = db.Column(db.String(255), unique=True)
    # confirmed_at = db.Column(db.DateTime())
    fullname = db.Column(db.String(50), nullable=False)

    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    # User information
    # active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    # first_name = db.Column(db.String(100), nullable=False, server_default='')
    # last_name = db.Column(db.String(100), nullable=False, server_default='')
    # Relationships
    # roles = db.relationship('Role', secondary='user_roles',
    #                         backref=db.backref('users', lazy='dynamic'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

# Define the Role data model
class Role(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


# Define the Vacation data model
class Vacation(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_date = db.Column(db.DateTime, default=datetime.today() + timedelta(days=1))
    to_date = db.Column(db.DateTime, default=datetime.today() + timedelta(days=8))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    # # Relationships
    # statuses = db.relationship('Status', secondary='vacation_status',
    #                         backref=db.backref('vacations', lazy='dynamic'))


# class VacationStatus(db.Model):
#     id = db.Column(db.Integer(), primary_key=True)
#     vacation_id = db.Column(db.Integer(), db.ForeignKey('vacation.id', ondelete='CASCADE'))
#     status_id = db.Column(db.Integer(), db.ForeignKey('status.id', ondelete='CASCADE'))


class Status(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    status_name = db.Column(db.String(50), unique=True)





mail = Mail(app)  # Initialize Flask-Mail


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


db.create_all()


def init_database():
    # newuser = User(username='default')
    s1 = Status(status_name='pending')
    s2 = Status(status_name='accepted')
    s3 = Status(status_name='declined')
    db.session.add(s1)
    db.session.add(s2)
    db.session.add(s3)
    # vacation.statuses.append(Status(status_name='pending'))
    # vacation.statuses.append(Status(status_name='accepted'))
    # vacation.statuses.append(Status(status_name='declined'))
    role1 = Role(name='viewer')
    role2 = Role(name='employee')
    role3 = Role(name='administrator')
    db.session.add(role1)
    db.session.add(role2)
    db.session.add(role3)
    # newuser.roles.append(Role(name='viewer'))
    # newuser.roles.append(Role(name='employee'))
    # newuser.roles.append(Role(name='administrator'))
    # vacation_status = VacationStatus()
    # vacation_status.append(VacationStatus(name='pending'))
    # vacation_status.append(VacationStatus(name='accepted'))
    # vacation_status.append(VacationStatus(name='declined'))
    # db.session.add(vacation)
    # db.session.add(newuser)
    db.session.commit()

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
user_manager = UserManager(db_adapter, app)  # Initialize Flask-User


redirect_uri = 'http://localhost:5000/gCallback'
client_id = '653118305882-1gi9758v39ahrck66fgt5eovj1vidtas.apps.googleusercontent.com'
client_secret = '72kErLTlV5R9z298cMOstnjN'

auth_uri = 'https://accounts.google.com/o/oauth2/auth'
token_uri = 'https://accounts.google.com/o/oauth2/token'
scope = ('https://www.googleapis.com/auth/userinfo.profile',
         'https://www.googleapis.com/auth/userinfo.email')
profile_uri = 'https://www.googleapis.com/oauth2/v1/userinfo'

# @app.route('/', defaults={'year': None})
# @app.route('/<int:year>/')
# @app.route('/')
# def index(year):
#     cal = Calendar(0)
#     try:
#         if not year:
#             year = date.today().year
#         cal_list = [
#             cal.monthdatescalendar(year, i + 1)
#             for i in range(12)
#             ]
#     except:
#         abort(404)
#     else:
#         return render_template('cal.html', year=year, cal=cal_list)
#     abort(404)


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


def get_user_id():
    flask_login.current_user.email
    user = User.query.filter(User.email==flask_login.current_user.email).first()
    return user.id


def redirect_to_user_page():
    return redirect(url_for('user_page', user_id=get_user_id()))

@app.route('/')
def index():
    if flask_login.current_user is not None and not flask_login.current_user.is_authenticated:
        return 'Please <a href="/login">login</a>'
    else:
        return redirect_to_user_page()
            # ('Hello <b>{}</b>.'
            #     '<a href="/logout">logout</a>').format(flask_login.current_user.email)




@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))


@app.route('/login')
def login():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('index'))
    # Step 1
    params = dict(response_type='code',
                  scope=' '.join(scope),
                  client_id=client_id,
                  approval_prompt='force',  # or 'auto'
                  redirect_uri=redirect_uri)
    try:
        url = auth_uri + '?' + urllib.urlencode(params)
        #Python version differentiation exception handling
    except:
        url = auth_uri + '?' + urllib.parse.urlencode(params)
    return redirect(url)


@app.route('/admin')
def admin():
    users = User.query.all()
    # user_list = ""
    # for user in users:
    #     user_list += "<a href ='/id/" + str(user.id) + "'>" + user.username + "</a><br>"
    # return 'Hello <b>admin</b>.<br><br>user list:<br>' + user_list + "<br><br><a href='/logout'>LOGOUT</a>"
    return render_template("admin.html",
                           users=users)

@app.route('/id/<user_id>/', methods=['GET', 'POST'])
def user_page(user_id):
    role_id = User.query.filter(User.email==flask_login.current_user.email).first().role_id
    user = User.query.filter_by(id=user_id).first()
    # context = user
    print(request.form)
    post = dict(request.form)
    print(post)

    # add new request
    if len(post) > 0:
        if 'new_request' in post['mytype']:
            from_date = datetime.strptime(post['from_date'][0], "%Y-%m-%d")
            to_date = datetime.strptime(post['to_date'][0], "%Y-%m-%d")
            vacation = Vacation(from_date=from_date, to_date=to_date, user_id=user_id, status_id=1)
            db.session.add(vacation)
            db.session.commit()
        modify = False
        status_id = 1
        if "accept" in post["mytype"]:
            modify = True
            status_id = 2
        if "decline" in post["mytype"]:
            modify = True
            status_id = 3
        if modify is True:
            vac_id = post["vac_id"][0]
            vacation = Vacation.query.filter(Vacation.id==int(vac_id)).first()
            vacation.status_id = status_id
            db.session.commit()
    # print(user.id)
    vacations = Vacation.query.filter(Vacation.user_id == user.id).order_by(Vacation.status_id, Vacation.from_date).all()
    # print(vacations)

    # adminUser = False
    datedefault_from = (datetime.today() + timedelta(days=1)).date()
    datedefault_to = (datetime.today() + timedelta(days=2)).date()
    # if user.role_id == 3:
    #     adminUser = True
    # print("vacations: " + str(vacations))
    status_query = Status.query.all()
    statuses = dict()
    for status in status_query:
        statuses[status.id] = status.status_name
    return render_template("user.html",
                           username=user.username,
                           user=user,
                           vacations=vacations,
                           main_role_id=role_id,
                           datedefault_from=datedefault_from,
                           datedefault_to=datedefault_to,
                           statuses=statuses,
                           back="/admin")
        #'<b>' + user.username + "</b>.<a href='/admin'>back</a>"




def create_newuser(rjson):
    try:
        email = rjson['email']
        username = email.split("@")[0]
        count = User.query.all()
        role_id = 1
        if len(count) == 0:
            role_id = 3
        if not User.query.filter(User.username == username).first():
            newuser = User(username=username,
                           email=email,
                           fullname=rjson['name'],
                           password=user_manager.hash_password(email),
                           role_id=role_id)
            db.session.add(newuser)
            db.session.commit()
    except Exception as e:
        print(str(e))


@app.route('/gCallback')
def gCallback():
    if flask_login.current_user.is_authenticated:
        return redirect_to_user_page()
    if 'code' in request.args:
        # Step 2
        code = request.args.get('code')
        data = dict(code=code,
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    grant_type='authorization_code')
                    # access_type='offline',
                    # include_granted_scopes="true")
                    # prompt='consent')
                    # approval_prompt='auto')
                    # access_type='online')
                    # grant_type='refresh_token')
                    # refresh_token=)
        r = requests.post(token_uri, data=data)
        # Step 3
        access_token = r.json()['access_token']
        r = requests.get(profile_uri, params={'access_token': access_token})
        user_data = r.json()
        email = user_data['email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User()
            user.email = email
        user.name = user_data['name']
        # try:
        #     token = google.fetch_token(
        #         token_uri,
        #         client_secret=client_secret,
        #         authorization_response=request.url)
        # except Exception as e:
        #     return 'HTTPError occurred.: ' + str(e)
        user.tokens = access_token
        user.avatar = user_data['picture']
        session['email'] = user_data['email']
        # session['']
        create_newuser(user_data)
        login_user(user)
        time.sleep(0.5)
        # login_user(user)
        print(str(r.json()))
        return redirect_to_user_page()
    else:
        return 'ERROR'


def add_new_group_member():
    r = requests.post('https://www.googleapis.com/admin/directory/v1/groups/invenshure_test/members', json={
           "email": "laszlo.benke@gravityrd.com",
            "role": "MEMBER"
    })
    print(r.json())

if __name__ == '__main__':
    try:
    #     add_new_group_member()
    #     print("added")

        if not Status.query.filter(Status.status_name == "pending").first():
            init_database()
        app.run(debug=True)
    except Exception as e:
        print(str(e))