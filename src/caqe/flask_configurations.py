"""
Configurations for Flask
"""

import os
from settings import SQLALCHEMY_DATABASE_URI, SERVER_NAME

try:
    from secret_keys import CSRF_SECRET_KEY, SESSION_KEY
except ImportError:
    try:
        CSRF_SECRET_KEY = os.environ['CSRF_SECRET_KEY']
        SESSION_KEY = os.environ['SESSION_KEY']
    except KeyError:
        raise KeyError('No keys found. Either define a secret_keys.py file (using generate_key_files.py) or set the '
                       'keys using environment variables.')


class Config(object):
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    CSRF_ENABLED = True


class Testing(Config):
    """
    For testing, add:

        0.0.0.0     caqe.local

    to /etc/hosts
    We need to set the SERVER_NAME to resolve `url_for` definitions when constructing the database, but we can't simply
    use `localhost` because the secure sessions are not compatible with that.
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SERVER_NAME = 'caqe.local:5000'


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SERVER_NAME = 'caqe.local:5000'


class Production(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SERVER_NAME = SERVER_NAME
    PREFERRED_URL_SCHEME = 'https'