#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create the database structure (clearing it if it already exists) and insert the tests and conditions as
defined in the test configuration (see :doc:`test_configurations`).

To run: ::

    $ python create_db.py

"""

from caqe import db
db.drop_all()
db.create_all()

import caqe
import caqe.experiment as experiment
with caqe.app.app_context():
    experiment.insert_tests_and_conditions()