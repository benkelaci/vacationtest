# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "wiehff76wteffu"

# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
# class ConfigClass(object):
#     # Flask settings
#     SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
#     SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vacation.sqlite')
#     CSRF_ENABLED = True
#
#     # Flask-Mail settings
#     MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'email@example.com')
#     MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'password')
#     MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"MyApp" <noreply@example.com>')
#     MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
#     MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
#     MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))
#
#     # Flask-User settings
#     USER_APP_NAME = "AppName"  # Used by email templates
#
# Secret key for signing cookies
SECRET_KEY = "2536t3vfjhds23"

REDIRECT_URI = 'http://localhost:5000/vacation/gCallback'
CLIENT_ID = '653118305882-1gi9758v39ahrck66fgt5eovj1vidtas.apps.googleusercontent.com'
CLIENT_SECRET = '72kErLTlV5R9z298cMOstnjN'

AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
SCOPE = ('https://www.googleapis.com/auth/userinfo.profile',
         'https://www.googleapis.com/auth/userinfo.email')
PROFILE_URI = 'https://www.googleapis.com/oauth2/v1/userinfo'