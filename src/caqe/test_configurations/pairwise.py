import os
from flask import url_for

# Set as production
PRODUCTION = os.getenv('FLASK_CONF') == 'PRODUCTION'

# Obtain consent from each participant (see consent.html)
OBTAIN_CONSENT = True

# Ask participants a survey before evaluation (see pre_test_survey.html)
PRE_TEST_SURVEY_ENABLED = True

# Ask participants a survey after evaluation (see post_test_survey.html)
POST_TEST_SURVEY_ENABLED = True

# Ask participants to complete the in-situ hearing response estimation
HEARING_RESPONSE_ESTIMATION_ENABLED = True

# The location of the production server
SERVER_NAME = ['caqe.local:5000', 'caqe.herokuapp.com'][PRODUCTION]

MTURK_HIT_PARAMETERS = {'question_url': 'https://%s/mturk' % SERVER_NAME,
                        'number_hits_approved_requirement': 1000,
                        'percent_assignments_approved_requirement': 97,
                        'title': 'Critical audio listening task. Listen to audio recordings and rate them on various '
                                 'scales of quality.',
                        'description': 'This listening test aims to rate the quality of a set of signals produced by '
                                       'source separation systems. Source separation aims to extract the signal of a '
                                       'target source from a mixture of several sound sources. The resulting signals may'
                                       ' include several types of degradations compared to the clean target source, '
                                       'including distortions of the target source, remaining sounds from other sources '
                                       'and additional artificial noise. Note that while the maximum number assignments '
                                       'a worker can do is 2, it\'s possible that fewer than 2 may be available to you. '
                                       '**CHROME ONLY** **BONUS AVAILABLE**',
                        'keywords': 'audio, sound, music, listening, research',
                        'assignmentDurationInSeconds': 60 * 30,  # 30 minutes
                        'lifetimeInSeconds': 60 * 60 * 24 * 7,  # 1 week
                        'maxAssignments': 80,
                        'autoApprovalDelayInSeconds': 60 * 60 * 24 * 1,  # 1 day
                        'reward': 0.50}  # USd (must convert to a boto.Price object)

POPUP_WIDTH = 1200
POPUP_HEIGHT = 1200

MTURK_DEBUG_FRAME_HEIGHT = 1200

# Test administrator's name
TEST_ADMIN_NAME = "<insert admin name here>"

# Test administrator's email
TEST_ADMIN_EMAIL = "<insert admin email here>"

# Enable participants to enter through '/anonymous'
ANONYMOUS_PARTICIPANTS_ENABLED = [True, False][PRODUCTION]

# This is the number of conditions to present to a participant in a single visit to '/evaluate'
CONDITIONS_PER_EVALUATION = 1

# The number of trials we should collect per condition (with distinct participants)
TRIALS_PER_CONDITION = 100

# Subject can only do one type of test
LIMIT_SUBJECT_TO_ONE_TASK_TYPE = True

# Save IP addresses of participants
IP_COLLECTION_ENABLED = True

# Randomize the condition order per test for each participant
TEST_CONDITION_ORDER_RANDOMIZED = True

# Randomize the stimulus order per for each condition
STIMULUS_ORDER_RANDOMIZED = True

# Hearing screening variables
# Set to True if you want the participants to be required to take a hearing screening test
HEARING_SCREENING_TEST_ENABLED = [False, True][PRODUCTION]
# The number of hours their hearing test is valid for (they must retake after this time has passed)
HEARING_TEST_EXPIRATION_HOURS = 24
# The number of attempts one has before they are sent away (they must wait `HEARING_TEST_EXPIRATION_HOURS`
# to take it again)
MAX_HEARING_TEST_ATTEMPTS = 2
# If this is set to True, then we still test the users, but we don't reject them...
HEARING_TEST_REJECTION_ENABLED = False  # True

# Hearing response estimation variables
HEARING_RESPONSE_NFREQS = 8  # number of different frequencies
HEARING_RESPONSE_NADD = 3  # number of max additional tones (60 for 10dB, 3 for 20dB Spacing)
N_OPTIONS = 20  # max number of frequencies for user to respond with in hearing response estimation

ENCRYPT_AUDIO_STIMULI_URLS = True

BEGIN_BUTTON_ENABLED = True

ACCEPTABLE_BROWSERS = ['chrome']  # set as None to disable browser rejection

TEST_TYPE = 'pairwise'

PREVIEW_HTML = """
    <p>A sound separation system aims to extract a clean recording of a single target sound (e.g. the vocalist) from a
    recording containing a mixture of several sounds (e.g. the rest of the band). This listening test aims to rate the
    quality of recordings produced by different sound separation systems. Due to imperfections of each sound separation
    system, the output recording (e.g. vocals extracted from the mixture) may include several types of degradations
    compared to the clean target sound&mdash;it might be a little distorted, you still might be able to hear the
    background (a little or a lot), it might have strange artifacts.</p>

    <p>During the test, you will be asked to assess the quality of the audio. The test will have three parts: 1) a short hearing
    test phase, 2) a training phase and 3) an evaluation phase. During the training phase, you will be trained on
    example ratings of quality. During the evaluation phase, you will listen to several of pairs of recordings and
    choose which recording in each pair has higher quality.</p>

    <p><b>You may receive up to a $0.25 bonus based on the consistency of your ratings.</b></p>

    <p>The expected total duration of the test is 5-7 minutes.</p>
    """


def is_pre_test_survey_valid(survey):
    """
    Make sure the participant meets the inclusion critera.

    Parameters
    ----------
    survey: dict

    Returns
    -------
    bool
    """
    if int(survey['age']) < 18:
        return False

    if survey['hearing_disorder'] == 'Yes':
        return False

    return True


def insert_tests_and_conditions():
    """
    This is where you configure and define the listening test.
    Running this doctest initializes the development database.

    Returns
    -------
    None

    Examples
    --------
    To call this you need the application context, e.g.:

    >>> import os
    >>> os.environ['FLASK_CONF'] = 'DEV' # for testing the Development configuration
    >>> from caqe import db
    >>> db.drop_all()
    >>> db.create_all()
    >>> import caqe
    >>> import caqe.settings
    >>> with caqe.app.app_context():
    ...     caqe.settings.insert_tests_and_conditions()
    """
    import json
    import caqe.models as models
    from caqe import db

    num_audio_files = 10

    # TEST VARIABLES
    default_test_vars = {'test_title': 'Task: Rate the <quality>',
                         'test_type': TEST_TYPE,
                         'randomize_test_order': True,
                         'test_timeout_sec': 5.,  # wait 5 seconds
                         'require_listening_to_all_training_sounds': False,  # True,
                         'references': (('Target', 'The target source which we are trying to isolate.'),
                                        ('Mixture', 'The mixture containing the target source and other sources.')),
                         'introduction_html': """
                                <p>A sound separation system aims to extract a clean recording of a single target sound
                                (e.g. the vocalist) from a recording containing a mixture of several sounds
                                (e.g. the rest of the band). This listening test aims to rate the quality of
                                recordings produced by different sound separation systems. Due to imperfections of each
                                sound separation system, the output recording (e.g. vocals extracted from the
                                mixture) may include several types of degradations compared to the clean target
                                sound&mdash;it might be a little distorted, you still might be able to hear the background
                                (a little or a lot), it might have strange artifacts.</p>

                                <p>During the test, you will be asked to assess the <quality>. The test will have three
                                parts: 1) a short hearing test phase, 2) a training phase and 3) an evaluation
                                phase. During the training phase, you will be trained on example ratings of quality.
                                During the evaluation phase, you will listen to several of pairs of recordings and
                                choose which recording in each pair has higher <quality>.</p>

                                <p><b>You may receive up to a $0.25 bonus based on the consistency of your ratings.</b></p>

                                <p>The expected total duration of the test is 5-7 minutes.</p>
                                """,
                         'first_task_introduction_html': """
                                <p>A sound separation system aims to extract a clean recording of a single target sound
                                (e.g. the vocalist) from a recording containing a mixture of several sounds
                                (e.g. the rest of the band). This listening test aims to rate the quality of
                                recordings produced by different sound separation systems. Due to imperfections of each
                                sound separation system, the output recording (e.g. vocals extracted from the
                                mixture) may include several types of degradations compared to the clean target
                                sound&mdash;it might be a little distorted, you still might be able to hear the background
                                (a little or a lot), it might have strange artifacts.</p>

                                <p>During the test, you will be asked to assess the <quality>. The test will have three
                                parts: 1) a short hearing test phase, 2) a training phase and 3) an evaluation
                                phase. During the training phase, you will be trained on example ratings of quality.
                                During the evaluation phase, you will listen to several of pairs of recordings and
                                choose which recording in each pair has higher <quality>. Lastly, at the end, there
                                will be a short survey which you will only have to fill out for the first HIT you
                                complete.</p>

                                <p><b>You may receive up to a $0.25 bonus based on the consistency of your ratings.</b></p>

                                <p>Including the survey at the end, the expected total duration of the first HIT is 8-10
                                minutes. Because this first HIT takes longer than the rest of the HITs in this group,
                                you will be given an additional $0.30 bonus on top of your consistency bonus.</p>
                                """,
                         'training_instructions_html': """
                                <p><quality_explanation></p>

                                <p>Instructions:
                                <ol>
                                <li>If you have not done so already, set the volume of your headphones/speakers so that
                                it's comfortable. You should be able to clearly hear differences between recordings
                                (the volume shouldn't be changed later on).</li>
                                <li>Train yourself on the example recordings to learn what types of recordings we
                                expect to be higher or lower than average according to the quality scale.</li>
                                </ol>
                                </p>
                         """,
                         'evaluation_instructions_html': """
                                <p>Listen to the Target and Mixture recordings below by clicking on their labeled
                                buttons. The Mixture and Target recordings will be the same for all pairs of
                                A/B recordings.</p>

                                <p>Listen to recordings A and B, and select which of the two recordings you would rate
                                as having higher <quality>. <quality_explanation></p>

                                <p>You can listen to the recordings as many times as you want before deciding.</p>
                         """}

    qualities = ['<b>overall quality</b> compared to the target sound for each recording',
                 'quality in terms of <b>preservation of the target sound</b> in each recording',
                 'quality in terms of <b>suppression of other sounds</b> in each recording',
                 'quality in terms of <b>absence of additional artificial noise</b> in each recording',
                 'quality in terms of <b>lack of distortions to the target sound</b> in each recording']

    quality_explanations = ['<b>Overall quality</b> refers to overall quality of the output of the sound separation '
                            'system, i.e. how well the target sound (e.g. a single voice) has been separated from the '
                            'mixture (e.g. a choir). Recordings should be rated based on how similar they are to the '
                            'target sound (e.g. the sound of a solo voice). For example, if a recording is very similar'
                            ' to the the target sound, it should be given a high rating. However, if a recording is '
                            'very different from the target sound (e.g. because of degradation or additional sounds), '
                            'it should be given a low rating.',
                            '<b>Preservation of the target sound</b> refers to how well the target sound (e.g. the '
                            'voice we\'re interested in isolating) has been preserved in the sound separation process. '
                            'For example, if the target sound is intact (but additional sounds possibly exist in the '
                            'recording), the recording should be given a high rating. However, if a recording is '
                            'missing parts of the target sound, it should be given a low rating.',
                            '<b>Suppression of other sound</b> refers to how well non-target sounds from the mixture '
                            'recording have been suppressed in the sound separation process. For example, if you cannot'
                            ' hear any of the non-target sounds from mixture in the recording, it should be given a '
                            'high rating (regardless of whether the target sound is well-preserved or not). However, '
                            'if many of the non-target sounds from the mixture are still in present in the recording, '
                            'it should be given a low rating.',
                            '<b>Absence of additional artificial noise</b> refers to the presence/absence of additional'
                            ' artificial noise that may have been introduced in the sound separation process. For '
                            'example, if a recording only contains sounds from the original mixture recording, it '
                            'should be given a high rating regardless of whether the target or non-target sounds are '
                            'completely intact. However, if the recording contains a lot of sounds (e.g. bleeps, '
                            'rumbles, pops) that are not in the original mixture, then the recording should be given a'
                            ' low rating.',
                            '<b>Lack of distortions to the target sound</b> refers to the amount of distortions to the'
                            ' target sound that may have been introduced in the sound separation process. For example,'
                            ' if the target sound is not distorted (regardless if other sounds from the mixture '
                            'recording are present), the recording should be given a high rating. However, if you '
                            'perceive the target sound as distorted in any way, it should be given a lower rating.']
    # THESE ARE THE TRAINING EXAMPLES
    reference_example_dict = [{'Target': url_for('static', filename='audio/exp00_target.wav'),
                               'Mixture': url_for('static', filename='audio/exp00_anchorInterf.wav')},
                              {'Target': url_for('static', filename='audio/exp00_target.wav'),
                               'Mixture': url_for('static', filename='audio/exp00_anchorInterf.wav')},
                              {'Target': url_for('static', filename='audio/exp00_target.wav'),
                               'Mixture': url_for('static', filename='audio/exp00_anchorInterf.wav')},
                              {'Target': url_for('static', filename='audio/exp00_target.wav'),
                               'Mixture': url_for('static', filename='audio/exp00_anchorInterf.wav')},
                              {'Target': url_for('static', filename='audio/exp00_target.wav'),
                               'Mixture': url_for('static', filename='audio/exp00_anchorInterf.wav')}]
    quality_example_dicts = [{'Low': [url_for('static', filename='audio/exp00_anchorInterf.wav'),
                                      url_for('static', filename='audio/exp00_anchorArtif.wav'),
                                      url_for('static', filename='audio/exp00_anchorDistTarget.wav')],
                              'High': [url_for('static', filename='audio/exp00_target.wav'), ]},
                             {'Low': [url_for('static', filename='audio/exp00_anchorDistTarget.wav')],
                              'High': [url_for('static', filename='audio/exp00_anchorInterf.wav'),
                                       url_for('static', filename='audio/exp00_anchorArtif.wav'),
                                       url_for('static', filename='audio/exp00_target.wav')]},
                             {'Low': [url_for('static', filename='audio/exp00_anchorInterf.wav'), ],
                              'High': [url_for('static', filename='audio/exp00_anchorArtif.wav'),
                                       url_for('static', filename='audio/exp00_anchorDistTarget.wav'),
                                       url_for('static', filename='audio/exp00_target.wav')]},
                             {'Low': [url_for('static', filename='audio/exp00_anchorArtif.wav'), ],
                              'High': [url_for('static', filename='audio/exp00_anchorInterf.wav'),
                                       url_for('static', filename='audio/exp00_anchorDistTarget.wav'),
                                       url_for('static', filename='audio/exp00_target.wav')]},
                             {'Low': [url_for('static', filename='audio/exp00_anchorArtif.wav'),
                                      url_for('static', filename='audio/exp00_anchorDistTarget.wav')],
                              'High': [url_for('static', filename='audio/exp00_anchorInterf.wav'),
                                       url_for('static', filename='audio/exp00_target.wav')]}]
    for quality, quality_explanation, reference_example_dict, quality_example_dict in zip(qualities,
                                                                                          quality_explanations,
                                                                                          reference_example_dict,
                                                                                          quality_example_dicts, ):
        test_name = default_test_vars['test_title'].replace('<quality>', quality)

        introduction_html = default_test_vars['introduction_html'].replace('<quality>', quality)
        introduction_html = introduction_html.replace('<quality_explanation>', quality_explanation)

        first_task_introduction_html = default_test_vars['first_task_introduction_html'].replace('<quality>', quality)
        first_task_introduction_html = first_task_introduction_html.replace('<quality_explanation>',
                                                                            quality_explanation)

        training_instructions_html = default_test_vars['training_instructions_html'].replace('<quality>',
                                                                                             quality)
        training_instructions_html = training_instructions_html.replace('<quality_explanation>',
                                                                        quality_explanation)

        evaluation_instructions_html = default_test_vars['evaluation_instructions_html'].replace('<quality>',
                                                                                                 quality)
        evaluation_instructions_html = evaluation_instructions_html.replace('<quality_explanation>',
                                                                            quality_explanation)

        test = models.Test(json.dumps(dict(default_test_vars,
                                           **{'quality_example_dict': quality_example_dict,
                                              'reference_example_dict': reference_example_dict,
                                              'test_title': test_name,
                                              'introduction_html': introduction_html,
                                              'first_task_introduction_html': first_task_introduction_html,
                                              'training_instructions_html': training_instructions_html,
                                              'evaluation_instructions_html': evaluation_instructions_html})))

        db.session.add(test)

    # save all tests
    db.session.commit()

    for test in models.Test.query.all():
        for j in range(1, num_audio_files + 1):
            # THE AUDIO STIMULUS FILES
            data = json.dumps({'reference_files': [('Target', 'exp%02d_target.wav' % j),
                                                   ('Mixture', 'exp%02d_anchorInterf.wav' % j)],
                               'stimulus_files': [('S1', 'exp%02d_target.wav' % j),
                                                  ('S2', 'exp%02d_anchorInterf.wav' % j),
                                                  ('S3', 'exp%02d_anchorArtif.wav' % j),
                                                  ('S4', 'exp%02d_anchorDistTarget.wav' % j),
                                                  ('S5', 'exp%02d_test5.wav' % j),
                                                  ('S6', 'exp%02d_test6.wav' % j),
                                                  ('S7', 'exp%02d_test7.wav' % j),
                                                  ('S8', 'exp%02d_test8.wav' % j)]})
            c = models.Condition(test_id=test.id, data=data)
            db.session.add(c)
            db.session.commit()
