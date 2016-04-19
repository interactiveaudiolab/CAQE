#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
create_db.py

"""

from caqe import db
db.drop_all()
db.create_all()

import caqe
import caqe.settings
with caqe.app.app_context():
    caqe.settings.insert_tests_and_conditions()