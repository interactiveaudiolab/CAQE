#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from flask import Flask
import os
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix

import caqe.configuration as configuration

__version__ = '0.1.1a1'
__title__ = 'CAQE'
__description__ = 'A crowdsourced audio quality evaluation toolkit.'
__uri__ = 'https://github.com/mcartwright/CAQE'
__author__ = 'Mark Cartwright'
__email__ = 'mcartwright@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2016 Mark Cartwright'

app = Flask('caqe')

app.config.from_object('caqe.configuration.BaseConfig')
app.config.from_pyfile('../test_configurations/' + os.getenv('CAQE_CONFIG', 'general_mushra.cfg'))

# Override variables based on APP_MODE
if configuration.APP_MODE == 'DEVELOPMENT':
    print('APP_MODE=DEVELOPMENT')
    app.config.from_object('caqe.configuration.DevelopmentOverrideConfig')
elif configuration.APP_MODE == 'TESTING':
    print('APP_MODE=TESTING')
    app.config.from_object('caqe.configuration.TestingOverrideConfig')
elif configuration.APP_MODE == 'PRODUCTION':
    print('APP_MODE=PRODUCTION')
    app.config.from_object('caqe.configuration.ProductionOverrideConfig')
    # On heroku, we must do a proxy fix, this enables to get the correct IP address from REMOTE_ADDR
    app.wsgi_app = ProxyFix(app.wsgi_app)
elif configuration.APP_MODE == 'EVALUATION':
    print('APP_MODE=EVALUATION')
    app.config.from_object('caqe.configuration.EvaluationDevOverrideConfig')


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
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)-8s: %(module)s:%(funcName)s - %(message)s')
        stream_handler.setFormatter(formatter)

        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)


import caqe.views
