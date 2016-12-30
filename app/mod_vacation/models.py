from app import db
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter, LoginManager
from datetime import datetime, timedelta


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

    def __repr__(self):
        return '<User %r>' % (self.username)


# Define the Role data model
class Role(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


    def __repr__(self):
        return '<Role %r>' % (self.name)


# Define the Vacation data model
class Vacation(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_date = db.Column(db.DateTime, default=datetime.today() + timedelta(days=1))
    to_date = db.Column(db.DateTime, default=datetime.today() + timedelta(days=8))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    def __repr__(self):
        return str(self.user_id)
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


# Build the database:
# This will create the database file using SQLAlchemy
if not Status.query.filter(Status.status_name == "pending").first():
    init_database()