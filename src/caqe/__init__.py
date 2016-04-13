__author__ = 'Mark Cartwright'

import logging
from flask import Flask
import os
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix

from settings import SQLALCHEMY_DATABASE_URI
import caqe.flask_configurations

app = Flask('caqe')

if os.getenv('FLASK_CONF') == 'DEV':
    print 'DEV'
    app.config.from_object('caqe.flask_configurations.Development')
elif os.getenv('FLASK_CONF') == 'TESTING':
    app.config.from_object('caqe.flask_configurations.Testing')
else:
    app.config.from_object('caqe.flask_configurations.Production')
    # On heroku, we must do a proxy fix, this enables to get the correct IP address from REMOTE_ADDR
    app.wsgi_app = ProxyFix(app.wsgi_app)

Bootstrap(app)
db = SQLAlchemy(app)

# MAKE SURE TO CREATE THE DATABASE - E.G. db.create_all()


@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    """
    This adds a hashvalue to the end of static resource that use the url_for to get their path. This is to cache bust
    when the file has been modified.
    """
    if 'static' == endpoint or '.static' == endpoint[-7:]:
        filename = values.get('filename', None)
        if filename:
            static_folder = app.static_folder

            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name

            values[param_name] = static_file_hash(os.path.join(static_folder, filename))

def static_file_hash(filename):
    return int(os.stat(filename).st_mtime) # or app.config['last_build_timestamp'] or md5(filename) or etc...


@app.before_first_request
def setup_logging():
    if not app.debug:
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)-8s: %(module)s:%(funcName)s - %(message)s')
        streamHandler.setFormatter(formatter)

        app.logger.addHandler(streamHandler)
        app.logger.setLevel(logging.INFO)

import caqe.views