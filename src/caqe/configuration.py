#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A app configuration defines the user-tunable parameters of the application and also the quality evaluation such as the:

* Amazon Mechanical Turk HIT description, pricing, keywords, etc.
* The description and instructions of the task
* The configuration of the type of test (e.g 'mushra' or 'pairwise')
* The definition of the quality scales
* The paths to the audio stimuli
* Which components of the evaluation are active (e.g. pre-test survey, post-test survey, hearing screening, etc.)

This subpackage contains a base configuration which contains overridable defaults, as well as pre-defined testing
configurations for common audio quality evaluation scenarios. Make sure that before you run a test that you at least
change the stimuli and the ``SERVER_ADDRESS`` variable.

.. seealso:: :doc:`../test_configurations`
"""

import os

try:
    from secret_keys import CSRF_SECRET_KEY, SESSION_KEY
except ImportError:
    try:
        CSRF_SECRET_KEY = os.environ['CSRF_SECRET_KEY']
        SESSION_KEY = os.environ['SESSION_KEY']
    except KeyError:
        raise KeyError('No keys found. Either define a secret_keys.py file (using generate_key_files.py) or set the '
                       'keys using environment variables.')

# Get the application mode from the environment variable APP_MODE
APP_MODE = os.getenv('APP_MODE')

# HEARING TEST CONSTANTS
MIN_HEARING_TEST_AUDIO_TONES = 2
MAX_HEARING_TEST_AUDIO_TONES = 8
HEARING_TEST_AUDIO_FILES_PER_TONES = 4
MIN_HEARING_TEST_AUDIO_INDEX = HEARING_TEST_AUDIO_FILES_PER_TONES * MIN_HEARING_TEST_AUDIO_TONES
MAX_HEARING_TEST_AUDIO_INDEX = HEARING_TEST_AUDIO_FILES_PER_TONES * MAX_HEARING_TEST_AUDIO_TONES

# HEARING RESPONSE ESTIMATION CONSTANTS
HEARING_RESPONSE_NFREQS = 8 # number of different frequencies
HEARING_RESPONSE_NADD = 3 # number of max additional tones (60 for 10dB, 3 for 20dB Spacing)


class BaseConfig(object):
    """
    The base application configuration.

    Attributes
    ----------
    DEBUG : bool
        Enable/disable debug mode (see Flask docs) (default is False)
    TESTING : bool
        Enable/disable testing mode (see Flask docs) (default is False)
    SECRET_KEY : str
        If a secret key is set, cryptographic components can use this to sign cookies and other things. Set this to a
        complex random value when you want to use the secure cookie for instance. Set via `generate_key_file.py` or
        using environment variable 'SECRET_KEY'. (see Flask Docs)
    CSRF_SESSION_KEY : str
        A Cross-site Request Forgery (CSRF) secret key for signing data. Set via `generate_key_file.py` or
        using environment variable 'CSRF_SESSION_KEY'. (see Flask docs)
    CSRF_ENABLED : bool
        Enable/disable protection against *Cross-site Request Forgery (CSRF)* (see Flask docs) (default is True)
    SERVER_ADDRESS : str
        The name and port number of the server. Do not include 'http'. (e.g.: 'caqe.local:5000') (see Flask docs)
        Can be set via environment variable 'SERVER_ADDRESS'. (default is 'caqe.local:5000')
    SQLALCHEMY_DATABASE_URI : str
        The database URI that should be used for the connection (see Flask-SQLAlchemy docs). Examples:
        * sqlite:////tmp/test.db
        * mysql://username:password@server/db
        Can be set via environment variable 'DATABASE_URL'. (default is'sqlite:////~/caqe.db')
    PREFERRED_URL_SCHEME : str
        The URL scheme that should be used for URL generation if no URL scheme is available. 'http' or 'https'
        (default is 'https')
    AUDIO_FILE_DIRECTORY : str
        Relative directory path to testing audio stimuli. (default is 'static/audio')
    ENCRYPT_AUDIO_STIMULI_URLS : bool
        Enable/disable encryption of the URLs so that users can't game consistency. (default is True)
    TEST_TYPE : str
        The test type (limited to 'pairwise' or 'mushra' for now). (default is None)
    ANONYMOUS_PARTICIPANTS_ENABLED : bool
        Enable/disable participants to enter through '/anonymous' entry point. (default is False)
    IP_COLLECTION_ENABLED : bool
        Enable/disable collection participants' IP addresses. (default is True)
    OBTAIN_CONSENT : bool
        If True, obtain consent from each participant (see consent.html) (default is True)
    PRE_TEST_SURVEY_ENABLED : bool
        If True, ask participants a survey before evaluation (see pre_test_survey.html). (default is True)
    PRE_TEST_SURVEY_INCLUSION_CRITERIA : list of str
        Pre-test survey inclusion criteria.
        (default is ["int(survey['age']) >= 18", "survey['hearing_disorder'] == 'No'"])
    POST_TEST_SURVEY_ENABLED : bool
        If True, ask participants a survey after evaluation (see post_test_survey.html) (default is True)
    HEARING_RESPONSE_ESTIMATION_ENABLED : bool
        If enabled, ask participants to complete the in-situ hearing response estimation. (default is True)
    CONDITIONS_PER_EVALUATION : int
        The number of conditions to present to a participant in a single visit to '/evaluate'.
        Note that currently evaluation is limited to one condition group. So if this value is more than 1, there must
        be at least as many conditions per group as there are conditions per evaluation for this to have an effect.
        It is also recommended that an integer multiple of `CONDITIONS_PER_EVALUATION` comprise the number of conditions
        per group. For example, if there are 28 conditions in a group, set the number of `CONDITIONS_PER_EVALUATION` to
        14 or 7.
        (default is 1)
    TRIALS_PER_CONDITION : int
        The number of trials we should collect per condition (with distinct participants). (default is 20)
    LIMIT_SUBJECT_TO_ONE_TASK_TYPE : bool
        If True, each subject is limited to one type of Test. (default is True)
    TEST_CONDITION_ORDER_RANDOMIZED : bool
        Randomize the condition order per test for each participant. (default is True)
    TEST_CONDITION_GROUP_ORDER_RANDOMIZED : bool
        Randomize the condition group order for each participant. (default is False)
    STIMULUS_ORDER_RANDOMIZED : bool
        Randomize the stimulus order per for each condition. (default is True)
    HEARING_SCREENING_TEST_ENABLED : bool
        Set to True if you want the participants to be required to take a hearing screening test. (default is True)
    HEARING_TEST_EXPIRATION_HOURS : int
        The number of hours their hearing test is valid for (they must retake after this time has passed)
        (default is 24)
    MAX_HEARING_TEST_ATTEMPTS : int
        The number of attempts one has before they are sent away (they must wait `hearing_test_expiration_hours`
        to take it again) (default is 2)
    HEARING_TEST_REJECTION_ENABLED : bool
        If this is set to True, then we still test the users, but we don't reject them. (default is True)
    HEARING_RESPONSE_NOPTIONS : int
        Max number of frequencies for user to respond with in hearing response estimation. (default is 20)
    MTURK_HOST : str
        Amazon Mechanical Turk host location. By default set it to the sandbox, and configure it via an environment
        variable (so, it can be easily modified when deploying and testing using Heroku).
        Can be set via environment variable 'MTURK_HOST'. (default is 'mechanicalturk.sandbox.amazonaws.com')
    MTURK_QUESTION_URL : str
        Entry point URL. (default is 'https://%s/mturk' % SERVER_ADDRESS)
    MTURK_REWARD : float
        This is the reward given to each worker for an approved assignment (in USD)
        (note that Amazon takes their Mechanical Turk Fee on top of this. See https://requester.mturk.com/pricing)
        (default is 0.50)
    MTURK_FIRST_HIT_BONUS : float
        The default bonus reward in USD that is optionally given (using ``turk_admin_cli.py``) to participants that
        completed the first assignment, which may have additional testing (e.g. survey, hearing tests, etc.)
        (default is 0.30)
    MTURK_MAX_CONSISTENCY_BONUS : float
        The defualt maximum bonus reward in USD for pairwise consistency. This optional bonus is given using
        ``turk_admin_cli.py``. (default is 0.25)
    MTURK_MIN_CONSISTENCY_THRESHOLD_FOR_BONUS : float
        The minimum pairwise consistency required to receive the optional bonus (given through ``turk_admin_cli.py``.)
        (default is 0.7)
    MTURK_NUMBER_HITS_APPROVED_REQUIREMENT : int
        MTurk worker must have this many approved HITs to accept task. (default is 1000)
    MTURK_PERCENT_ASSIGNMENTS_APPROVED_REQUIREMENT : int
        MTurk worker must have this percentage of approved assignments to accept task. (default is 97)
    MTURK_TITLE : str
        Title of MTurk HIT (default is 'Critical audio listening task. Listen to audio recordings and rate them on
        various scales of quality.')
    MTURK_DESCRIPTION : str
        Description of MTurk HIT.
        (default is 'This listening test aims to rate the quality of a set of signals in comparison to a reference
        signal. Note that while the maximum number assignments a worker can do is 10, it's possible that fewer than
        10 may be available to you. \*\*CHROME ONLY\*\* \*\*BONUS AVAILABLE\*\*')
    MTURK_KEYWORDS : str
        Keywords for MTurk HIT. (default is 'audio, sound, music, listening, research')
    MTURK_ASSIGNMENT_DURATION_IN_SECONDS : int
        Accepted MTurk assignments must be completed within this duration or they will be released to other workers
        (default is 60 * 30, i.e. 30 minutes)
    MTURK_LIFETIME_IN_SECONDS : int
        HITs expire (no one can accept them) after this duration since being posted.
        (default is 60 * 60 * 24 * 7, i.e 1 week)
    MTURK_FRAME_HEIGHT : int
        The size of the Mechanical Turk browser frame (default is 1200)
    ACCEPTABLE_BROWSERS : list of str
        The set of acceptable browsers. set as None to disable browser rejection. (default is ['chrome',])
    BEGIN_BUTTON_ENABLED : bool
        If true, participants will have to click a button that launches a new window. This is useful in order to
        delay condition assignment until the user is engaged in the task, and allows a new window to be launched
        that is bigger than the Mechanical Turk frame for instance. (default is True)
    POPUP_WIDTH : int
        The width of the window launched when participants press the "begin button" the task. (default is 1200)
    POPUP_HEIGHT : int
        The height of the window launched when participants press the "begin button" the task. (default is 1200)
    TEST_TIMEOUT_SEC : float
        The participant must spend at least this amount of time on the evaluation task before submission.
        (default is 60.)
    REQUIRE_LISTENING_TO_ALL_TRAINING_SOUNDS : bool
        If True, the participant must listen to all of the training sounds before proceeding to the evaluation task.
        (default is True)
    PREVIEW_HTML : str
        The HTML content of the preview page. This will be the same for all conditions, regardless of test since
        conditions are assigned on the fly (so we can have complete control over condition assignment).
        (default is None)
    MIN_RATING_VALUE : int
        The minimum rating value on the MUSHRA slider. (default is 0)
    MAX_RATING_VALUE : int
        The maximum rating value on the MUSHRA slider. (default is 99)
    DEFAULT_RATING_VALUE : int
        The default rating value on the MUSHRA slider. (default is 50)
    TESTS : list of dict
        The test and condition-specific configuration variables.
        Note that if 'evaluation_instructions_html' is not None in the condition, it will override the instructions
        defined in the test.
        Note also that reference keys must be alphanumeric and stimulus keys must begin with 'S' followed by a number,
        e.g. 'S29'.

        The dicts are of the form::

            {'test_config_variables':
                {'test_title': '...', # The test title that is displayed on the evaluation page
                 'first_task_introduction_html': '...',  # Content of the intro page the first time they do a task
                 'introduction_html': '...', # Content of the intro page (after the first time they perform the task)
                 'training_instructions_html': '...', # The HTML content of the training instructions
                 'evaluation_instructions_html': '...'}, # The HTML content of the evaluation instructions
                 'references' : (('<reference_name>', '<reference_description>'),), # Reference names and descriptions
                 'reference_example_dict':
                    {'<reference_name}': url_for('static', filename='audio/<reference_filename>.wav'), ... },
                 'quality_example_dict':
                    {'<example_type0>': [url_for('static', filename='audio/<example0_filename>.wav'),
                                         url_for('static', filename='audio/<example1_filename>.wav'),],
                     '<example_type1>': [url_for('static', filename='audio/<example3_filename>),]}},
             'condition_groups' :
                [{'reference_files': {<reference_name>: '<reference_filename>.wav',},
                 {'stimulus_files': {'S1': '<S1_filename>.wav',
                                     'S2': '<S2_filename>,wav',}},
                 {'conditions': [{'reference_keys': [<reference_name>,],
                                  'stimulus_keys': ['S1','S2','S7', ... ],
                                  'evaluation_instructions_html': <condition_specific_evaluation_instructions>},]},]}

        (default is [])


    Note
    ----
    For testing, add: ::

        0.0.0.0     caqe.local

    to /etc/hosts
    We need to set the SERVER_ADDRESS to resolve ``url_for`` definitions when constructing the database, but we can't simply
    use `localhost` because the secure sessions are not compatible with that.
    """
    # ---------------------------------------------------------------------------------------------
    # BACKEND VARIABLES
    TESTING = False
    DEBUG = False
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////%s' % os.path.expanduser('~/caqe.db'))
    SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', 'caqe.local:5000')
    PREFERRED_URL_SCHEME = 'https'
    AUDIO_FILE_DIRECTORY = os.getenv('AUDIO_FILE_DIRECTORY', 'static/audio')
    AUDIO_CODEC = 'wav'
    ENCRYPT_AUDIO_STIMULI_URLS = True
    EXTERNAL_FILE_HOST = False
    BEGIN_TITLE = 'Audio Quality Evaluation'

    # ---------------------------------------------------------------------------------------------
    # TESTING VARIABLES
    TEST_TYPE = None
    ANONYMOUS_PARTICIPANTS_ENABLED = False
    IP_COLLECTION_ENABLED = True
    OBTAIN_CONSENT = False
    PRE_TEST_SURVEY_ENABLED = True
    PRE_TEST_SURVEY_INCLUSION_CRITERIA = ["int(survey['age']) >= 18",
                                          "survey['hearing_disorder'] == 'No'"]
    POST_TEST_SURVEY_ENABLED = True
    HEARING_RESPONSE_ESTIMATION_ENABLED = True
    CONDITIONS_PER_EVALUATION = 1
    TRIALS_PER_CONDITION = 20
    LIMIT_SUBJECT_TO_ONE_TASK_TYPE = True
    TEST_CONDITION_ORDER_RANDOMIZED = True
    TEST_CONDITION_GROUP_ORDER_RANDOMIZED = False
    STIMULUS_ORDER_RANDOMIZED = True

    # ---------------------------------------------------------------------------------------------
    # HEARING SCREENING VARIABLES
    HEARING_SCREENING_TEST_ENABLED = True
    HEARING_TEST_EXPIRATION_HOURS = 12
    MAX_HEARING_TEST_ATTEMPTS = 2
    HEARING_TEST_REJECTION_ENABLED = True

    # ---------------------------------------------------------------------------------------------
    # HEARING RESPONSE ESTIMATION VARIABLES
    HEARING_RESPONSE_NOPTIONS = 20

    # ---------------------------------------------------------------------------------------------
    # MECHANICAL TURK VARIABLES
    MTURK_HOST = os.getenv('MTURK_HOST', 'mechanicalturk.sandbox.amazonaws.com')
    MTURK_QUESTION_URL = 'https://%s/mturk' % SERVER_ADDRESS
    MTURK_REWARD = 0.50
    MTURK_FIRST_HIT_BONUS = 0.30
    MTURK_MAX_CONSISTENCY_BONUS = 0.25
    MTURK_MIN_CONSISTENCY_THRESHOLD_FOR_BONUS = 0.7
    MTURK_NUMBER_HITS_APPROVED_REQUIREMENT = 1000
    MTURK_PERCENT_ASSIGNMENTS_APPROVED_REQUIREMENT = 97
    MTURK_TITLE = 'Critical audio listening task. Listen to audio recordings and rate them on various ' \
                  'scales of quality.'
    MTURK_DESCRIPTION = 'This listening test aims to rate the quality of a set of signals in comparison to a reference ' \
                        'signal. Note that while the maximum number assignments a worker can do is 10, it\'s possible that ' \
                        'fewer than 10 may be available to you. **CHROME ONLY** **BONUS AVAILABLE**'
    MTURK_KEYWORDS = 'audio, sound, music, listening, research'
    MTURK_ASSIGNMENT_DURATION_IN_SECONDS = 60 * 30
    MTURK_LIFETIME_IN_SECONDS = 60 * 60 * 24 * 7
    MTURK_MAX_ASSIGNMENTS = 200
    MTURK_AUTO_APPROVAL_DELAY_IN_SECONDS = 60 * 60 * 24 * 1  # 1 day
    MTURK_FRAME_HEIGHT = 1200

    # ---------------------------------------------------------------------------------------------
    # FRONT-END VARIABLES
    ACCEPTABLE_BROWSERS = ['chrome']
    BEGIN_BUTTON_ENABLED = True
    POPUP_WIDTH = 1200
    POPUP_HEIGHT = 1200
    TEST_TIMEOUT_SEC = 60.
    REQUIRE_LISTENING_TO_ALL_TRAINING_SOUNDS = True
    PREVIEW_HTML = None
    MIN_RATING_VALUE = 0
    MAX_RATING_VALUE = 99
    DEFAULT_RATING_VALUE = 50

    # ---------------------------------------------------------------------------------------------
    # DEFAULT CONDITION AND TEST-SPECIFIC VARIABLES
    #   (These will be configured for each condition and saved in the database)
    TESTS = []


class TestingOverrideConfig(object):
    """
    Override config for testing.

    Note
    ----
    To enable these parameters set environment variable ``APP_MODE`` to 'TESTING'. In Linux: ::

        $ export APP_MODE=TESTING

    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SERVER_ADDRESS = 'caqe.local:5000'
    MTURK_QUESTION_URL = 'https://%s/mturk' % SERVER_ADDRESS
    PREFERRED_URL_SCHEME = 'http'


class DevelopmentOverrideConfig(object):
    """
    Override config for development.

    Note
    ----
    To enable these parameters set environment variable ``APP_MODE`` to 'DEVELOPMENT'. In Linux: ::

        $ export APP_MODE=DEVELOPMENT

    """
    DEBUG = True
    SERVER_ADDRESS = 'caqe.local:5000'
    MTURK_QUESTION_URL = 'https://%s/mturk' % SERVER_ADDRESS
    HEARING_TEST_REJECTION_ENABLED = False
    PREFERRED_URL_SCHEME = 'http'
    REQUIRE_LISTENING_TO_ALL_TRAINING_SOUNDS = False


class ProductionOverrideConfig(object):
    """
    Override config for production.

    Note
    ----
    To enable these parameters set environment variable ``APP_MODE`` to 'PRODUCTION'. In Linux: ::

        $ export APP_MODE=PRODUCTION

    """
    TESTING = False
    DEBUG = False


class EvaluationDevOverrideConfig(object):
    """
    Override config for evaluation task development.

    Note
    ----
    To enable these parameters set environment variable ``APP_MODE`` to 'EVALUATION'. In Linux: ::

        $ export APP_MODE=EVALUATION

    """
    DEBUG = True
    SERVER_ADDRESS = 'caqe.local:5000'
    MTURK_QUESTION_URL = 'https://%s/mturk' % SERVER_ADDRESS
    HEARING_TEST_REJECTION_ENABLED = False
    HEARING_SCREENING_TEST_ENABLED = False
    HEARING_RESPONSE_ESTIMATION_ENABLED = False
    PREFERRED_URL_SCHEME = 'http'
    REQUIRE_LISTENING_TO_ALL_TRAINING_SOUNDS = False
    PRE_TEST_SURVEY_ENABLED = False
    POST_TEST_SURVEY_ENABLED = False
