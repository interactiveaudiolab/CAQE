"""
experiment.py

Contains functions related to the experimental design of the listening test
"""
import copy
import json
import logging
import random
import datetime
import itertools

from sqlalchemy import func

from settings import *
import utilities

from models import Condition, Participant, Trial
from caqe import db

logger = logging.getLogger(__name__)


def get_available_conditions(limit_to_condition_ids=None):
    """
    Get conditions available without regard to participant.

    Parameters
    ----------
    limit_to_condition_ids: list of int
        List of conditions ids to limit to.

    Returns
    -------
    conditions
        The available conditions
    """
    finished_conditions = db.session.query(Trial.condition_id).filter(Trial.participant_passed_hearing_test == True). \
        group_by(Trial.condition_id).having(func.count('*') >= CONFIGURATION['trials_per_condition']).subquery()

    conditions = db.session.query(Condition).filter(Condition.id.notin_(finished_conditions))

    if limit_to_condition_ids is not None:
        conditions = conditions.filter(Condition.id.in_(limit_to_condition_ids))

    conditions = conditions.order_by(Condition.id)

    return conditions


def assign_conditions(participant, limit_to_condition_ids=None):
    """
    Assign experimental conditions for a participant's trial.

    Parameters
    ----------
    participant : caqe.models.Participant
    limit_to_condition_ids : list, optional
        List of integer ids.

    Returns
    -------
    condition_ids : list of ints
    """
    # Ideal assignment in our scenario:
    # If the participant passed the listening test:
    # Assign a participant the first condition (in order of index) that has
    #   A) not been assigned to them before
    #   B) has not received the required number of ratings by people that have passed the listening test
    # If the participant has not passed the listening test:
    #   Same as above. This may give us a bit more ratings from lower condition indices for people that have not passed
    #   the listening test, but I think that is ok.

    # construct our subqueries
    # conditions which have the required number of trials with hearing_test passed participants
    conditions = get_available_conditions(limit_to_condition_ids)

    # the conditions the participant has already done
    participant_conditions = db.session.query(Trial.condition_id).join(Participant). \
        filter(Participant.id == participant.id).subquery()

    conditions = conditions.filter(Condition.id.notin_(participant_conditions))

    # conditions = db.session.query(Condition). \
    #     filter(and_(Condition.id.notin_(finished_conditions),
    #                 Condition.id.notin_(participant_conditions),
    #                 Condition.id.in_([2, 12, 22, 32, 42, 5, 15, 25, 35, 45]))). \
    #     order_by(Condition.id).all()
    conditions = conditions.order_by(Condition.id).all()

    if conditions is None or len(conditions) == 0:
        logger.info('No hits left for %r' % participant)
        return None

    if CONFIGURATION['limit_subject_to_one_task_type']:
        previous_trial = participant.trials.filter(Trial.datetime_completed > datetime.datetime(2015, 5, 25)).first()
        try:
            if previous_trial.condition.test_id != conditions[0].test_id:
                # If the participant is supposed to be limited to one task type, and we are out of all task of that type
                logger.info('Subject limited to ont task type. No hits left for %r' % participant)
                return None
        except AttributeError:
            # no previous trials
            pass

    if CONFIGURATION['test_condition_order_randomized']:  # i.e. randomize the condition order within a test
        # determine what test we are on
        current_test_id = conditions[0].test_id

        # randomize the order of the conditions within that test
        condition_ids = [c.id for c in conditions if c.test_id == current_test_id]
        random.shuffle(condition_ids)
        condition_ids = condition_ids[:CONFIGURATION['conditions_per_evaluation']]

        # if there are not enough conditions left from this test, add more from the next.
        if len(condition_ids) < CONFIGURATION['conditions_per_evaluation']:
            more_cids = [c.id for c in conditions if c.test_id == current_test_id + 1]
            random.shuffle(more_cids)
            condition_ids += more_cids[:(CONFIGURATION['conditions_per_evaluation'] - len(condition_ids))]
    else:
        condition_ids = [c.id for c in conditions[:CONFIGURATION['conditions_per_evaluation']]]

    logger.info('Participant %r assigned conditions: %r' % (participant, condition_ids))
    return condition_ids


def get_test_configurations(condition_ids, participant_id):
    """
    Generate template configuration variables from the list of experimental conditions.

    Parameters
    ----------
    condition_ids : list
    participant_id : int

    Returns
    -------
    test_configuration : list of list of dicts
        A list of dictionaries containing all the configuration variables for each test, including a list of conditions
        and their variables
    """
    test_configurations = []

    current_test_id = None
    test_config = None
    for c_id in condition_ids:
        condition = Condition.query.filter_by(id=c_id).first()
        if condition.test_id != current_test_id:
            if test_config is not None:
                test_configurations.append(test_config)
            current_test_id = condition.test_id
            test_config = {'test': json.loads(condition.test.data),
                           'conditions': []}

        condition_data = json.loads(condition.data)
        # make sure that condition_id is added to the conditions dict
        if CONFIGURATION['encrypt_audio_stimuli_urls']:
            condition_data['reference_files'] = encrypt_audio_stimuli(condition_data['reference_files'],
                                                                      participant_id,
                                                                      condition.id)
            condition_data['stimulus_files'] = encrypt_audio_stimuli(condition_data['stimulus_files'],
                                                                     participant_id,
                                                                     condition.id)
        test_config['conditions'].append(dict({'id': condition.id}, **condition_data))
    test_configurations.append(test_config)

    return test_configurations


def generate_comparison_pairs(condition_datas):
    """
    Generate all stimulus comparison pairs for a condition and return in a random order for a paired comparison test.

    Parameters
    ----------
    condition_datas: list of dict
        List of dictionary of condition data as returned in the test_configuration defined by get_test_configurations()

    Returns
    -------
    condition_datas: list of dict
        List of updated dictionary of condition data with a new field, `comparison_pairs`, which is a list of stimulus
        pairs, e.g. (('E1','E2'),('E5','E8'),...)
    """
    for condition_data in condition_datas:
        stimulus_names = [c[0] for c in condition_data['stimulus_files']]
        pairs = []
        for x in itertools.combinations(stimulus_names, 2):
            if random.randint(0, 1):
                pairs.append(x)
            else:
                pairs.append(x[::-1])
        random.shuffle(pairs)
        condition_data['comparison_pairs'] = pairs

    return condition_datas


def encrypt_audio_stimuli(audio_stimuli, participant_id, condition_id):
    """
    Reorder and encrypt the condition files. Do this by encoding each file as a special URL. One in which is an
    encrypted, serialized, dictionary. The dictionary contains, the participant_id (p_id), the condition_id (c_id),
    the stimuli_id (s_id), and a encrypted stimuli_id (e_id)

    Parameters
    ----------
    audio_stimuli: list of duples
        The first element of each duple is a key, the second is the audio_file_path
        For all non-references, the key should be of the form S[0-9+]
    participant_id: int
    condition_id: int

    Returns
    -------
    encrypted_audio_stimuli: list of duples
        The first element of each duple is a key, the second is the encrypted audio_file_path
        For all non-references, the key should be of the form E[0-9+]. The order of the stimuli will be random (except
        for the references)
    """

    def encode_url(url, _s_id, _e_id):
        adict = {'s_id': _s_id,
                 'p_id': participant_id,
                 'c_id': condition_id,
                 'e_id': _e_id,
                 'URL': url}
        return '/audio/' + utilities.encrypt_data(adict) + '.wav'

    audio_stimuli = copy.deepcopy(audio_stimuli)

    references = [(a[0], encode_url(a[1], a[0], a[0])) for a in audio_stimuli if a[0][0] != 'S']

    non_references = [a for a in audio_stimuli if a[0][0] == 'S']

    if CONFIGURATION['stimulus_order_randomized']:
        random.shuffle(non_references)

    for k, a in enumerate(non_references):
        e_id = 'E%d' % (k + 1)
        s_id = a[0]
        a[0] = e_id
        a[1] = encode_url(a[1], s_id, e_id)

    return references + non_references


def decrypt_audio_stimuli(condition_data):
    """
    Decrypt the audio stimuli URLs from submitted trial data

    Parameters
    ----------
    condition_data: dict
        The condition data with encrypted audio URLs

    Returns
    -------
    trial_data: dict
    """

    def decode_url(encrypted_url):
        # remove /audio/
        encrypted_data = encrypted_url[7:]
        # remove .wav
        encrypted_data = encrypted_data[:-4]
        return utilities.decrypt_data(str(encrypted_data))

    if not CONFIGURATION['encrypt_audio_stimuli_urls']:
        return condition_data
    encrypted_filenames = condition_data['stimulusFiles']
    decrypted_filenames = {}
    translation = {}

    # decrypt the URLs to find the mapping between s_id and e_id and the real filename
    for k, v in encrypted_filenames.items():
        adict = decode_url(v)
        decrypted_filenames[adict['s_id']] = adict['URL']
        translation[adict['e_id']] = adict['s_id']

    condition_data['stimulusFiles'] = decrypted_filenames

    if CONFIGURATION['test_type'] == 'mushra':
        condition_data['ratings'] = dict([(translation[k], v) for k, v in condition_data['ratings'].items()])
    elif CONFIGURATION['test_type'] == 'pairwise':
        ratings_dict = {}
        for k, v in condition_data['ratings'].items():
            ratings_dict[k] = {'stimuli': [translation[v['stimuli'][0]],
                                           translation[v['stimuli'][1]]],
                               'selection': v['selection']}
        condition_data['ratings'] = ratings_dict
    return condition_data


def is_pre_test_survey_valid(survey, inclusion_criteria):
    """
    Make sure the participant meets the inclusion critera.

    Parameters
    ----------
    survey: dict
    inclusion_criteria: list
        List of expressions as strings which we will evaluate. If any of these inclusion criteria are False,
        return False.

    Returns
    -------
    bool
    """
    for ic in inclusion_criteria:
        if not eval(ic):
            return False

    return True
