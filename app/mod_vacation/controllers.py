# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from app import db

# Import module forms
# from app.mod_vacation.forms import LoginForm

# Import module models (i.e. User)
from app.mod_vacation.models import User, Vacation, Role, Status
from app import login_manager

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
from flask_login import login_user
import flask_login
from datetime import datetime, timedelta
import json
import time
from flask import current_app


# Define the blueprint: 'vacation', set its url prefix: app.url/vacation
mod_vacation = Blueprint('vacation', __name__, url_prefix='/vacation')

#
# @mod_vacation.record
# def record_params(setup_state):
#     app = setup_state.app
#     mod_vacation.config = dict([(key,value) for (key,value) in app.config.iteritems()])
# from flask_user import UserManager, UserMixin, SQLAlchemyAdapter, LoginManager




@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

def get_user_id():
    user = User.query.filter(User.email==flask_login.current_user.email).first()
    return user.id


def redirect_to_user_page():
    return redirect(url_for('vacation.user_page', user_id=get_user_id()))

@mod_vacation.route('/')
def index():
    if flask_login.current_user is not None and not flask_login.current_user.is_authenticated:
        return 'Please <a href="/vacation/login">login</a>'
    else:
        return redirect_to_user_page()
            # ('Hello <b>{}</b>.'
            #     '<a href="/logout">logout</a>').format(flask_login.current_user.email)




@mod_vacation.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('vacation.index'))


@mod_vacation.route('/login')
def login():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('vacation.index'))
    # Step 1
    params = dict(response_type='code',
                  scope=' '.join(current_app.config.get("SCOPE")),
                  client_id=current_app.config.get("CLIENT_ID"),
                  approval_prompt='force',  # or 'auto'
                  redirect_uri=current_app.config.get("REDIRECT_URI"))
    try:
        url = current_app.config.get("AUTH_URI") + '?' + urllib.urlencode(params)
        #Python version differentiation exception handling
    except:
        url = current_app.config.get("AUTH_URI") + '?' + urllib.parse.urlencode(params)
    return redirect(url)


@mod_vacation.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.all()
    # user_list = ""
    # for user in users:
    #     user_list += "<a href ='/id/" + str(user.id) + "'>" + user.username + "</a><br>"
    # return 'Hello <b>admin</b>.<br><br>user list:<br>' + user_list + "<br><br><a href='/logout'>LOGOUT</a>"
    return render_template("admin.html",
                           users=users,
                           adminuser=flask_login.current_user)

@mod_vacation.route('/id/<user_id>/', methods=['GET', 'POST'])
def user_page(user_id):
    try:
        if flask_login.current_user.email is not None:
            role_id = User.query.filter(User.email == flask_login.current_user.email).first().role_id
    except Exception as e:
        role_id = 1
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
        else:
            new_role_id = 1
            if "viewer" in post["mytype"]:
                modify = True
            if "employee" in post["mytype"]:
                modify = True
                new_role_id = 2
            if modify is True:
                user_id = post["user_id"][0]
                user = User.query.filter(User.id == int(user_id)).first()
                user.role_id = new_role_id
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
    role_name = Role.query.filter(Role.id==user.role_id).first().name
    return render_template("user.html",
                           username=user.username,
                           user=user,
                           vacations=vacations,
                           main_role_id=role_id,
                           user_role_name=role_name,
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
                           # password=user_manager.hash_password(email),
                           password=email,
                           role_id=role_id)
            db.session.add(newuser)
            db.session.commit()
    except Exception as e:
        print(str(e))


@mod_vacation.route('/gCallback')
def gCallback():
    if flask_login.current_user.is_authenticated:
        return redirect_to_user_page()
    if 'code' in request.args:
        # Step 2
        code = request.args.get('code')
        data = dict(code=code,
                    client_id=current_app.config.get("CLIENT_ID"),
                    client_secret=current_app.config.get("CLIENT_SECRET"),
                    redirect_uri=current_app.config.get("REDIRECT_URI"),
                    grant_type='authorization_code')
                    # access_type='offline',
                    # include_granted_scopes="true")
                    # prompt='consent')
                    # approval_prompt='auto')
                    # access_type='online')
                    # grant_type='refresh_token')
                    # refresh_token=)
        r = requests.post(current_app.config.get("TOKEN_URI"), data=data)
        # Step 3
        access_token = r.json()['access_token']
        r = requests.get(current_app.config.get("PROFILE_URI"), params={'access_token': access_token})
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
        # time.sleep(0.5)
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
