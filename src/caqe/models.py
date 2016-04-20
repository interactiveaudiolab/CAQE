#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLAlchemy database models
"""
import datetime
import uuid
import logging

from caqe import db
from caqe import app

logger = logging.getLogger(__name__)


class Participant(db.Model):
    """
    A participant in an experiment

    Attributes
    ----------
    id : int
        Primary key
    ip_address : str
        The IP address of the participant
    crowd_worker_id : str
        The crowdsourcing site ID, e.g. Amazon MTurk's workerId
    platform : str
        The platform the participant came from, e.g. ANONYMOUS, M_TURK, etc.
    passed_hearing_test : bool
        The user has passed the hearing test
    gave_consent : bool
        Participant agreed to the consent form.
    hearing_test_attempts : int
        The number of hearing_test_attempts
    hearing_test_last_attempt : DateTime
        The DateTime of the last hearing test attempt (pass or fail)
    pre_test_survey : str
        Pre-test survey data in JSON
    post_test_survey : str
        Post-test survey data in JSON
    hearing_response_estimation : str
        Hearing response estimation data in JSON
    """
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45))
    crowd_worker_id = db.Column(db.String(256), unique=True)
    platform = db.Column(db.String(128))
    passed_hearing_test = db.Column(db.Boolean, default=False)
    gave_consent = db.Column(db.Boolean, default=False)
    hearing_test_attempts = db.Column(db.Integer, default=0)
    hearing_test_last_attempt = db.Column(db.DateTime, default=datetime.datetime(1, 1, 1))
    pre_test_survey = db.Column(db.Text, default=None)
    post_test_survey = db.Column(db.Text, default=None)
    hearing_response_estimation = db.Column(db.Text, default=None)
    trials = db.relationship('Trial', backref='participant', lazy='dynamic')

    def __init__(self, platform, crowd_worker_id=None, ip_address=None):
        self.platform = platform
        if crowd_worker_id is None or crowd_worker_id == 'ANONYMOUS':
            self.crowd_worker_id = uuid.uuid4().hex
        else:
            self.crowd_worker_id = crowd_worker_id
        if app.config['IP_COLLECTION_ENABLED']:
            self.ip_address = ip_address

    def __repr__(self):
        return "<Participant id=%r, platform=%r, crowd_worker_id=%r>" % (self.id, self.platform, self.crowd_worker_id)

    def has_passed_hearing_test_recently(self):
        """
        Check to see if participant has passed the hearing test recently (as defined in settings.py)

        Returns
        -------
        bool
        """
        if (datetime.datetime.now() - self.hearing_test_last_attempt) \
                >= datetime.timedelta(hours=app.config['HEARING_TEST_EXPIRATION_HOURS']):
            self.passed_hearing_test = False
            self.hearing_test_attempts = 0

            # regardless of HEARING_TEST_REJECTION_ENABLED or not, if they haven't taken the test recently, have
            # them take it again
            return self.passed_hearing_test
        else:
            # regardless if they have taken the test recently, if HEARING_TEST_REJECTION_ENABLED is False, let them
            # through
            return self.passed_hearing_test or not app.config['HEARING_TEST_REJECTION_ENABLED']

    def set_passed_hearing_test(self, passed_hearing_test):
        """
        Mark them as having passed the hearing test

        Parameters
        ----------
        passed_hearing_test : bool

        Returns
        -------
        None
        """
        self.hearing_test_last_attempt = datetime.datetime.now()
        self.hearing_test_attempts += 1
        self.passed_hearing_test = passed_hearing_test


class Test(db.Model):
    """
    An experimental test. Many conditions may share these properties.

    Attributes
    ----------
    id: int
        Primary key
    data: str
        JSON-encoded string of formatted test variables
    """
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    conditions = db.relationship('Condition', backref='test', lazy='dynamic')

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "<Test id=%r, data=%r>" % (self.id, self.data)


class Condition(db.Model):
    """
    An experimental condition, i.e. the variable conditions of a trial

    Attributes
    ----------
    id : int
        Primary key
    test_id: int, optional
        Foreign key to the Test the condition belongs to
    data : str
        JSON-enconded string of formatted condition variables
    """
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    data = db.Column(db.Text)
    trials = db.relationship('Trial', backref='condition', lazy='dynamic')

    def __init__(self, data, test_id=None):
        self.data = data
        self.test_id = test_id

    def __repr__(self):
        return "<Condition id=%r, data=%r>" % (self.id, self.data)


class Trial(db.Model):
    """
    A trial in an experiment

    Attributes
    ----------
    id : int
        Primary key
    participant_id : int
        Foreign key to the Participant of the trial
    condition_id : int
        Foreign key to the Condition of the trial
    crowd_data : str
        JSON-encoded string of data from the crowdsourcing site (e.g. workerId, assignmentId, HITId, etc. from MTurk)
    data : str
        JSON-enconded string formatted trial data dictionary
    participant_passed_hearing_test: bool
        Participant passed hearing test at time of trial
    """
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    condition_id = db.Column(db.Integer, db.ForeignKey('condition.id'))
    crowd_data = db.Column(db.Text)
    data = db.Column(db.Text)
    participant_passed_hearing_test = db.Column(db.Boolean)
    datetime_completed = db.Column(db.DateTime)

    def __init__(self, participant_id, condition_id, data, crowd_data=None, participant_passed_hearing_test=None):
        self.participant_id = participant_id
        self.condition_id = condition_id
        self.data = data
        self.crowd_data = crowd_data
        self.participant_passed_hearing_test = participant_passed_hearing_test
        self.datetime_completed = datetime.datetime.now()

    def __repr__(self):
        return "<Trial id=%r, participant_id=%r, condition_id=%r, " \
               "participant_passed_hearing_test=%r, datetime_completed=%r>" % \
               (self.id,
                self.participant_id,
                self.condition_id,
                self.participant_passed_hearing_test,
                self.datetime_completed)
