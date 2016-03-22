__author__ = 'Mark Cartwright'

"""
create_db.py

"""

from ceaq import db
db.drop_all()
db.create_all()

import ceaq
import ceaq.settings
with ceaq.app.app_context():
    ceaq.settings.insert_tests_and_conditions()