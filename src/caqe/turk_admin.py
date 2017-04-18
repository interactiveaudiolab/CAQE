#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Amazon Mechanical Turk administration. Use this module to post, approve, expire, and bonus HITs.
"""
import json
import datetime

import numpy as np
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.qualification import Qualifications, NumberHitsApprovedRequirement, \
    PercentAssignmentsApprovedRequirement
from boto.mturk.price import Price
from boto.mturk.question import ExternalQuestion

import caqe.models as models
from caqe import app

try:
    from secret_keys import AWS_ACCESS_KEY_ID, AWS_SECRET_KEY
except ImportError:
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_KEY = None
    raise ImportError('In order to run Amazon Mechanical Turk administration tasks, you must provide your credentials '
                      'in `secret_keys.py`.')


def turk_connect():
    """
    Connect to Mechanical Turk and return a connection. This uses `AWS_ACCESS_KEY_ID` and `AWS_SECRET_KEY` from
    `secret_keys.py` (you must put these in yourself).

    Returns
    -------
    boto.MTurkConnection
    """
    return MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_KEY,
                           host=app.config['MTURK_HOST'])


def calculate_tsr(ratings, stimuli=('S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8')):
    """
    Calculate the Transitivity Satisfaction Rate (TSR) for a group of ratings.

    Parameters
    ----------
    ratings : dict
        Ratings dictionary
    stimuli : tuple of str
        Tuple of stimulus identifiers in order.

    Returns
    -------
    float
        The TSR.
    """
    n = len(stimuli)
    m = np.zeros([n, n])
    for k, r in ratings.items():
        m[stimuli.index(r['stimuli'][0]), stimuli.index(r['stimuli'][1])] = r['selection'] == 'A'
        m[stimuli.index(r['stimuli'][1]), stimuli.index(r['stimuli'][0])] = not (r['selection'] == 'A')
    n_test = 0
    n_pass = 0
    for i in range(0, n - 1):
        for j in range(0, n - 1):
            for k in range(0, n - 1):
                if i == j or j == k:
                    continue
                if m[i, j] == 1 and m[j, k] == 1:
                    n_test += 1
                    if m[i, k] == 1:
                        n_pass += 1
    return float(n_pass) / n_test, n_pass, n_test, m


def confirm_reference():
    return True


class TurkAdmin(object):
    """
    Instantiate this class to connect to MTurk and perform administrative tasks.
    """

    def __init__(self, debug=False):
        self.connection = turk_connect()
        self._hit_type_id = None
        self.debug = debug
        print app.config['MTURK_HOST']

        self.all_hit_types = [self.hit_type_id, ]

    def create_hits(self, num_hits, configuration=None, hit_type_id=None):
        """
        Create `num_audio_hits` according to the parameters specified in `hit_params`

        Parameters
        ----------
        num_hits: int
        configuration: dict
        hit_type_id: int, optional

        Returns
        -------
        None
        """
        if configuration is None:
            configuration = app.config

        if hit_type_id is None:
            hit_type_id = self.hit_type_id
        question = ExternalQuestion(configuration['MTURK_QUESTION_URL'],
                                    frame_height=configuration['MTURK_FRAME_HEIGHT'])
        for _i in range(num_hits):
            self.connection.create_hit(hit_type=hit_type_id,
                                       question=question,
                                       lifetime=configuration['MTURK_LIFETIME_IN_SECONDS'],
                                       max_assignments=configuration['MTURK_MAX_ASSIGNMENTS'], )

    def register_hit(self, configuration=None):
        """
        Register a hit on Mechanical Turk according to `hit_params`. This will provide you with a HITTypeId.

        Parameters
        ----------
        configuration : dict

        Returns
        -------
        str
            The HITTypeId which is how you refer to your newly registered hit with Amazon
        """
        if configuration is None:
            configuration = app.config

        qualifications = Qualifications()
        if self.debug:
            qualifications.add(NumberHitsApprovedRequirement('GreaterThanOrEqualTo', 0))
            qualifications.add(PercentAssignmentsApprovedRequirement('GreaterThanOrEqualTo', 0))
        else:
            qualifications.add(NumberHitsApprovedRequirement('GreaterThanOrEqualTo',
                                                             configuration['MTURK_NUMBER_HITS_APPROVED_REQUIREMENT']))
            qualifications.add(PercentAssignmentsApprovedRequirement('GreaterThanOrEqualTo',
                                                                     configuration[
                                                                         'MTURK_PERCENT_ASSIGNMENTS_APPROVED_REQUIREMENT']))

        hit_type = self.connection.register_hit_type(configuration['MTURK_TITLE'],
                                                     configuration['MTURK_DESCRIPTION'],
                                                     Price(configuration['MTURK_REWARD']),
                                                     configuration['MTURK_ASSIGNMENT_DURATION_IN_SECONDS'],
                                                     configuration['MTURK_KEYWORDS'],
                                                     configuration['MTURK_AUTO_APPROVAL_DELAY_IN_SECONDS'],
                                                     qualifications)
        return hit_type[0].HITTypeId

    def _get_hit_type_id(self):
        if self._hit_type_id is None:
            self._hit_type_id = self.register_hit()
        return self._hit_type_id

    hit_type_id = property(fget=_get_hit_type_id)

    def filter_hits(self, hits, hit_types=None):
        """
        Return the hits whose type is in `hit_types`

        Parameters
        ----------
        hits : list of boto.HIT
        hit_types : list of str

        Returns
        -------
        list of boto.HIT
        """
        if hit_types is None:
            hit_types = [self.hit_type_id]
        return [hit for hit in hits if hit.HITTypeId in hit_types]

    def expire_all_hits(self):
        """
        Expire all hits

        Returns
        -------
        None
        """
        for hit in self.connection.get_all_hits():
            try:
                self.connection.expire_hit(hit.HITId)
            except Exception as e:
                print e

    def expire_hits(self, hit_types=None):
        """
        Expire all hits whose HITTypeId is in `hit_types`

        Parameters
        ----------
        hit_types : list of str, optional

        Returns
        -------
        None
        """
        # todo: doc
        if hit_types is None:
            hit_types = self.all_hit_types
        for hit in self.filter_hits(self.connection.get_all_hits(), hit_types):
            self.connection.expire_hit(hit.HITId)

    def dispose_hits(self, hit_types=None):
        """
        Dispose all hits whose HITTypeId is in `hit_types` (Disposing a HIT removes it from the system).

        Parameters
        ----------
        hit_types : list of str, optional

        Returns
        -------
        None
        """
        # todo: doc
        if hit_types is None:
            hit_types = self.all_hit_types
        for hit in self.filter_hits(self.connection.get_all_hits(), hit_types):
            self.connection.dispose_hit(hit.HITId)

    def dispose_all_hits(self):
        """
        Dispose all hits

        Returns
        -------
        None
        """
        for hit in self.connection.get_all_hits():
            try:
                self.connection.dispose_hit(hit.HITId)
            except Exception as e:
                print e

    def get_assignments_to_review(self, hit_type, page_size=100, page_number=1):
        """
        Get assignments to review for the specified HIT type given page size and page number

        Parameters
        ----------
        hit_type : str
            HITTypeId
        page_size : int
            How many assignments to return
        page_number : int
            What page of assignments to return

        Returns
        -------
        assignments : list of boto.Assignment
        """
        hits = self.connection.get_reviewable_hits(hit_type=hit_type)
        assignments = []
        for hit in hits:
            assignments.extend(self.connection.get_assignments(hit.HITId, page_size=page_size, page_number=page_number))
        return assignments

    def get_all_assignments(self):
        """
        Get all assignments regardless of HIT type

        Returns
        -------
        assignments : list of boto.Assignment
        """
        hits = self.connection.get_all_hits()
        assignments = []
        for hit in hits:
            page = 1
            while True:
                page_assignments = self.connection.get_assignments(hit.HITId, page_size=100, page_number=page)
                assignments.extend(page_assignments)
                page += 1
                if len(page_assignments) == 0:
                    break
        return assignments

    def get_all_assignments_to_review(self, hit_type, status=('Submitted', 'Approved', 'Rejected')):
        """
        Get *all* the assignments to review for the specified HIT type

        Parameters
        ----------
        hit_type : str
        status : str, optional
            Assignment status. Valid values are 'Submitted', 'Approved', 'Rejected'.

        Returns
        -------
        assignments: list of boto.Assignment
        """
        assignments = []
        page_number = 1
        while True:
            # NOTE: this will retrieve all reviewable assignments (in Submitted, Approve, Rejected states)
            page_assignments = [a for a in self.get_assignments_to_review(hit_type, 100, page_number) if
                                a.AssignmentStatus in status]
            assignments.extend(page_assignments)
            page_number += 1
            if len(page_assignments) == 0:
                break
        return assignments

    def approve_all(self, hit_types=None):
        """
        Approve all 'Submitted' assignments

        Parameters
        ----------
        hit_types : list of str, optional

        Returns
        -------
        None
        """
        if hit_types is None:
            hit_types = self.all_hit_types
        assignments = self.get_all_assignments()
        for a in assignments:
            if a.AssignmentStatus == 'Submitted':
                hit = self.connection.get_hit(a.HITId)[0]
                if hit.HITTypeId in hit_types:
                    self.connection.approve_assignment(a.AssignmentId, 'Thank you!')

    def force_approve_all(self):
        """
        Approve all 'Submitted' assignments

        Returns
        -------
        None
        """
        assignments = self.get_all_assignments()
        for a in assignments:
            if a.AssignmentStatus == 'Submitted':
                self.connection.approve_assignment(a.AssignmentId, 'Thank you!')

    def get_completion_times(self, assignments=None):
        """
        Compute completion time of `assignments`. The completion time is the time between when the HIT was
        accepted and submitted.

        Parameters
        ----------
        assignments : list of Assignment, optional
            The list of assignments to compute average completion time. If None, then compute on all assignments.
            Default is None.

        Returns
        -------
        times : list of float
            The list of completion times in seconds.
        """
        if assignments is None:
            assignments = self.get_all_assignments()
        times = []
        for a in assignments:
            if a.AssignmentStatus == 'Submitted' or a.AssignmentStatus == 'Approved':
                fmt = '%Y-%m-%dT%H:%M:%SZ'
                x = datetime.datetime.strptime(a.SubmitTime, fmt)
                y = datetime.datetime.strptime(a.AcceptTime, fmt)
                times.append((x - y).seconds)
        return times

    def give_bonus_to_all_first_completed_trials(self,
                                                 price=app.config['MTURK_FIRST_HIT_BONUS'],
                                                 calculate_amt_only=False,
                                                 reason=None,
                                                 already_bonused_ids=set()):
        """
        Grant bonuses for the first completed trial for each participant.

        Parameters
        ----------
        price : float, optional
            The bonus amount to grant in dollars. Default is defined by the CAQE configuration.
        calculate_amt_only : bool, optional
            Only calculate the amount of the bonus, do not actual pay out the bonus.
        reason : str, optional
            The message to send the workers when they receive the bonus
        already_bonused_ids : set, optional
            Set of participant ids that have already been bonused


        Returns
        -------
        total_bonus: float
            The total amount paid
        participants_wo_valid_asgnmts: list of caqe.models.Participant
            The participants who did not have valid assignments in their trial data (e.g. there must have been an error
            when submitting the assignment)

        """
        if reason is None:
            reason = "Thanks for completing our Critical Audio Listening Task HIT. This bonus is to compensate you " \
                     "for the extra time needed to complete the first assignment of the HIT."

        total_bonus = 0
        participants_wo_valid_asgnmts = []
        participants = models.Participant.query.all()
        for p in participants:
            if p.id in already_bonused_ids:
                continue
            trials = p.trials.all()
            if len(trials) > 0:
                bonus_paid = False
                for t in trials:
                    try:
                        print p.id
                        crowd_data = json.loads(t.crowd_data)

                        assignment_id = crowd_data['assignment_id']
                        worker_id = p.crowd_worker_id
                        if not calculate_amt_only:
                            self.connection.grant_bonus(worker_id, assignment_id, Price(price), reason)
                        total_bonus += price
                        bonus_paid = True
                        break
                    except MTurkRequestError as e:
                        print e
                        continue
                if not bonus_paid:
                    participants_wo_valid_asgnmts.append(p)
        return total_bonus, participants_wo_valid_asgnmts

    def give_consistency_bonus(self,
                               max_price=app.config['MTURK_MAX_CONSISTENCY_BONUS'],
                               threshold=app.config['MTURK_MIN_CONSISTENCY_THRESHOLD_FOR_BONUS'],
                               calculate_amt_only=False,
                               reason=None,
                               already_bonused_ids=set()):
        """
        Grant bonuses based on ratings consistency. Bonus calculated by

        .. math:: ((consistency - threshold) / (1.0 - threshold)) * max\_price * (consistency > threshold))

        Parameters
        ----------
        max_price : float, optional
            The maximum bonus amount to grant in dollars. Default is defined by the CAQE configuration.
        threshold : bool
            Consistency must exceed this value before a bonus is paid out. Default is defined by the CAQE configuration.
        calculate_amt_only : bool, optional
            Only calculate the amount of the bonus, do not actual pay out the bonus.
        reason : str, optional
            The message to send the workers when they receive the bonus
        already_bonused_ids : set, optional
            Set of participant ids that have already been bonused


        Returns
        -------
        total_bonus : float
            The total amount paid
        participants_wo_valid_asgnmts : list of caqe.models.Participant
            The participants who did not have valid assignments in their trial data (e.g. there must have been an error
            when submitting the assignment)

        """
        if reason is None:
            reason = "Thanks for completing our Critical Audio Listening Task HIT. This bonus is to award you for " \
                     "your consistency in ratings during the task."
        total_bonus = 0
        trials_wo_valid_asgnmts = []
        trials = models.Trial.query.all()
        for t in trials:
            if t.id in already_bonused_ids:
                continue
            try:
                crowd_data = json.loads(t.crowd_data)
                data = json.loads(t.data)
                assignment_id = crowd_data['assignment_id']
                worker_id = t.participant.crowd_worker_id
                consistency = calculate_tsr(data['rating'])[0]
                price = round(
                    abs(((consistency - threshold) / (1.0 - threshold)) * max_price * (consistency > threshold)), 2)
                if not calculate_amt_only and price > 0.0:
                    print price
                    self.connection.grant_bonus(worker_id, assignment_id, Price(price), reason)
                total_bonus += price
            except MTurkRequestError as e:
                print e
                trials_wo_valid_asgnmts.append(t)
        return total_bonus, trials_wo_valid_asgnmts

