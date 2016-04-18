"""
The base CAQE configuration from which the other configurations are derived.
"""

import os

# Set as production
PRODUCTION = os.getenv('FLASK_CONF') == 'PRODUCTION'

SERVER_NAME = ['caqe.local:5000', 'caqe.herokuapp.com'][PRODUCTION]

# CONFIGURATION contains all of the configurable values for the test. For each condition
CONFIGURATION = {
    # ---------------------------------------------------------------------------------------------
    # BACKEND VARIABLES
    # The location of the production server
    'server_name': SERVER_NAME,

    # Encrypt the URLs so that users can't game consistency
    'encrypt_audio_stimuli_urls': True,

    # ---------------------------------------------------------------------------------------------
    # TESTING VARIABLES
    # The test type (limited to 'pairwise' or 'mushra' for now)
    'test_type': None,

    # Enable participants to enter through '/anonymous'
    'anonymous_participants_enabled': [True, False][PRODUCTION],

    # Save IP addresses of participants
    'ip_collection_enabled': True,

    # Obtain consent from each participant (see consent.html)
    'obtain_consent': True,

    # Ask participants a survey before evaluation (see pre_test_survey.html)
    'pre_test_survey_enabled': True,

    # Pre-test survey inclusion criteria
    'pre_test_survey_inclusion_criteria': ["int(survey['age']) >= 18",
                                           "survey['hearing_disorder'] == 'No'"],

    # Ask participants a survey after evaluation (see post_test_survey.html)
    'post_test_survey_enabled': True,

    # Ask participants to complete the in-situ hearing response estimation
    'hearing_response_estimation_enabled': True,

    # This is the number of conditions to present to a participant in a single visit to '/evaluate'
    'conditions_per_evaluation': 1,

    # The number of trials we should collect per condition (with distinct participants)
    'trials_per_condition': 20,

    # Subject can only do one type of test
    'limit_subject_to_one_task_type': True,

    # Randomize the condition order per test for each participant
    'test_condition_order_randomized': True,

    # Randomize the stimulus order per for each condition
    'stimulus_order_randomized': True,

    # ---------------------------------------------------------------------------------------------
    # HEARING SCREENING VARIABLES
    # Set to True if you want the participants to be required to take a hearing screening test
    'hearing_screening_test_enabled': [False, True][PRODUCTION],

    # The number of hours their hearing test is valid for (they must retake after this time has passed)
    'hearing_test_expiration_hours': 24,

    # The number of attempts one has before they are sent away (they must wait `hearing_test_expiration_hours`
    # to take it again)
    'max_hearing_test_attempts': 2,

    # If this is set to True, then we still test the users, but we don't reject them...
    'hearing_test_rejection_enabled': True,

    # ---------------------------------------------------------------------------------------------
    # HEARING RESPONSE ESTIMATION VARIABLES
    # number of different frequencies
    'hearing_response_nfreqs': 8,

    # number of max additional tones (60 for 10dB, 3 for 20dB Spacing)
    'hearing_response_nadd': 3,

    # max number of frequencies for user to respond with in hearing response estimation
    'n_options': 20,

    # ---------------------------------------------------------------------------------------------
    # MECHANICAL TURK VARIABLES
    # Entry point URL
    'question_url': 'https://%s/mturk' % SERVER_NAME,

    # This is the reward given to each worker for an approved assignment
    # (note that Amazon takes their Mechanical Turk Fee on top of this. See https://requester.mturk.com/pricing)
    'reward': 0.50,  # USD (must convert to a boto.Price object)

    # MTurk worker must have this many approved HITs to accept task
    'number_hits_approved_requirement': 1000,

    # MTurk worker must have this percentage of approved assignments to accept task
    'percent_assignments_approved_requirement': 97,

    # Title of MTurk HIT
    'title': 'Critical audio listening task. Listen to audio recordings and rate them on various '
             'scales of quality.',

    # Description of MTurk HIT
    'description': 'This listening test aims to rate the quality of a set of signals in comparison to a reference '
                   'signal. Note that while the maximum number assignments a worker can do is 10, it\'s possible that '
                   'fewer than 10 may be available to you. '
                   '**CHROME ONLY** **BONUS AVAILABLE**',

    # Keywords for MTurk HIT
    'keywords': 'audio, sound, music, listening, research',

    # Accepted MTurk assignments must be completed within this duration or they will be released to other workers
    'assignmentDurationInSeconds': 60 * 30,  # 30 minutes

    # HITs expire (no one can accept them) after this duration since being posted
    'lifetimeInSeconds': 60 * 60 * 24 * 7,  # 1 week

    # The maximum number of assignments per HIT. Since we are handling condition assignment on our end (not using
    # Amazon's mechanism), this the total number of trials (i.e. no. of conditions * no. of assignments per condition)
    #  that we are collecting.
    'maxAssignments': 200,

    # If we do not review this assignments in this time period, the assignment will be automatically approved and the
    # worker will be paid.
    'autoApprovalDelayInSeconds': 60 * 60 * 24 * 1,  # 1 day

    # ---------------------------------------------------------------------------------------------
    # FRONT-END VARIABLES
    # The set of acceptable browsers. set as None to disable browser rejection
    'acceptable_browsers': ['chrome'],

    # If true, participants will have to click a button that launches a new window. This is useful in order to
    # delay condition assignment until the user is engaged in the task, and allows a new window to be launched
    # that is bigger than the Mechanical Turk frame for instance.
    'begin_button_enabled': True,

    # The size of the window launched when participants press the "begin button" the task.
    'popup_width': 1200,
    'popup_height': 1200,

    # The participant must spend at least this amount of time on the evaluation task before submission
    'test_timeout_sec': 60.,  # wait 60 seconds

    # If True, the participant must listen to all of the training sounds before proceeding to the evaluation task
    'require_listening_to_all_training_sounds': True,

    # The reference stimuli in the evaluation task
    'references': (('Reference', 'The reference signal to which test signals are compared.'),),

    # The HTML content of the preview page. This will be the same for all conditions, regardless of test since
    # conditions are assigned on the fly (so we can have complete control over condition assignment).
    'preview_html': None,

    # ---------------------------------------------------------------------------------------------
    # DEFAULT CONDITION AND TEST-SPECIFIC VARIABLES
    #   (These will be configured for each condition and saved in the database)

    # The test title that is displayed on the evaluation page
    'test_title': None,

    # The HTML content of the introduction page the first time they do a task
    'first_task_introduction_html': None,

    # The HTML content of the introduction page (after the first time they perform the task)
    'introduction_html': None,

    # The HTML content of the training instructions
    'training_instructions_html': None,

    # The HTML content of the evaluation instructions
    'evaluation_instructions_html': None
}