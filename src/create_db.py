#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
create_db.py

"""

from caqe import db
db.drop_all()
db.create_all()

import caqe
import caqe.experiment as experiment
with caqe.app.app_context():
    experiment.insert_tests_and_conditions()