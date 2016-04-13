__author__ = 'Mark Cartwright'

"""
settings.py

Settings for CEAQ. These are for the CEAQ user to configure.
"""
import os

# Set as production
PRODUCTION = os.getenv('FLASK_CONF') == 'PRODUCTION'

# The location of the database.
# For a temporary database, set this to 'sqlite://'
# If the environment variable DATABASE_URL is set, it uses that instead (e.g. on Heroku)
if os.environ.get('DATABASE_URL') is not None:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s' % os.path.expanduser('~/caqe.db')

URL_SCHEME = ['http', 'https'][PRODUCTION]

# Amazon Mechanical Turk settings
MTURK_HOST = os.getenv('MTURK_HOST', 'mechanicalturk.sandbox.amazonaws.com')

# Audio file directory
AUDIO_FILE_DIRECTORY = 'static/audio'

from caqe.test_configurations.pairwise import *



