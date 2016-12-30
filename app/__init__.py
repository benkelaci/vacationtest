# Import flask and template operators
from flask import Flask, render_template
# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter, LoginManager



# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


from app.mod_vacation.models import User

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_vacation.controllers import mod_vacation


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404



# Register blueprint(s)
app.register_blueprint(mod_vacation)
# app.register_blueprint(xyz_module)
# ..


db.create_all()


# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
# user_manager = UserManager(db_adapter, app)  # Initialize Flask-User

