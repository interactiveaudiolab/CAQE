"""
A general MUSHRA (MUltiple Stimulus Hidden Reference and Anchor) configuration for evaluating overall quality
of a set of audio stimuli.
"""

import copy
from flask import url_for

import caqe.test_configurations.base
from caqe.test_configurations.base import SERVER_NAME

# CONFIGURATION contains all of the configurable values for the test. For each condition
CONFIGURATION = copy.deepcopy(caqe.test_configurations.base.CONFIGURATION)
CONFIGURATION = dict(CONFIGURATION, **{
    # ---------------------------------------------------------------------------------------------
    # TESTING VARIABLES
    # The test type (limited to 'pairwise' or 'mushra' for now)
    'test_type': 'mushra',

    # ---------------------------------------------------------------------------------------------
    # FRONT-END VARIABLES
    # The minimum rating value on the MUSHRA slider
    'min_rating_value': 0,

    # The maximum rating value on the MUSHRA slider
    'max_rating_value': 99,

    # The default rating value on the MUSHRA slider
    'default_rating_value': 50,

    # The participant must spend at least this amount of time on the evaluation task before submission
    'test_timeout_sec': 60.,  # wait 60 seconds

    # The HTML content of the preview page. This will be the same for all conditions, regardless of test since
    # conditions are assigned on the fly (so we can have complete control over condition assignment).
    'preview_html':
        """
        <p>This listening test aims to rate the quality of a set of signals in comparison to a reference signal.</p>

        <p>During the test, you will be asked to assess the quality of the audio. The test will have three parts: 1)
        a short hearing test phase, 2) a training phase and 3) an evaluation phase. During the training phase, you
        will have to listen to all the recordings and learn the range of quality that is possible. During the
        evaluation phase, you will have to rate the quality of eight test recordings compared to the perfect target
        sound.</p>

        <p>The expected total duration of the test is 5 minutes.</p>
        """,

    # ---------------------------------------------------------------------------------------------
    # DEFAULT CONDITION AND TEST-SPECIFIC VARIABLES
    #   (These will be configured for each condition and saved in the database)

    # The test title that is displayed on the evaluation page
    'test_title': 'Task: Rate the <quality>',

    # The HTML content of the introduction page the first time they do a task
    'first_task_introduction_html':
        """
        <p>This listening test aims to rate the quality of a set of signals in comparison to a reference signal.</p>

        <p>During the test, you will be asked to assess the quality of the audio. The test will have three parts: 1)
        a short hearing test phase, 2) a training phase and 3) an evaluation phase. During the training phase, you
        will have to listen to all the recordings and learn the range of quality that is possible. During the
        evaluation phase, you will have to rate the quality of eight test recordings compared to the perfect target
        sound. Lastly, at the end, there will be a short survey which you will only have to fill out for the first HIT
        you complete.</p>

        <p>Including the survey at the end, the expected total duration of the first HIT is 8 minutes. Because this
        first HIT takes longer than the rest of the HITs in this group, you will be given a $0.30 bonus.</p>
        """,

    # The HTML content of the introduction page (after the first time they perform the task)
    'introduction_html':
        """
        <p>This listening test aims to rate the quality of a set of signals in comparison to a reference signal.</p>

        <p>During the test, you will be asked to assess the quality of the audio. The test will have three parts: 1)
        a short hearing test phase, 2) a training phase and 3) an evaluation phase. During the training phase, you
        will have to listen to all the recordings and learn the range of quality that is possible. During the
        evaluation phase, you will have to rate the quality of eight test recordings compared to the perfect target
        sound.</p>

        <p>The expected total duration of the test is 5 minutes.</p>
        """,

    # The HTML content of the training instructions
    'training_instructions_html':
        """
        <p><quality_explanation></p>

        <p>Instructions:
        <ol>
        <li>If you have not done so already, set the volume of your headphones/speakers so that
        it's comfortable. You should be able to clearly hear differences between recordings
        (the volume shouldn't be changed later on).</li>
        <li>You must fully listen to all of the recordings before proceeding to the next
        section.</li>
        <li>Train yourself on the example recordings to learn what types of recordings we
        expect to receive a higher or lower than average rating according to the quality scale.</li>
        <li>Train yourself to notice the <quality> and learn the range of <quality>.</li>
        </ol>
        </p>
         """,

    # The HTML content of the evaluation instructions
    'evaluation_instructions_html':
        """
        <p><b>Rate the <quality> on a scale from 0 to 100</b>, where larger ratings indicate
        better quality. <quality_explanation></p>

        <p>You can listen to the recordings as many times as you want before deciding. Once you
        have rated all recordings, listen to them again to make sure that the ratings between
        pairs of recordings are consistent, i.e. if one recording has better quality than
        another, it should be rated higher.</p>
        """
})


# Configure and insert conditions
def insert_tests_and_conditions():
    """
    This is where you configure and define the listening test. If you need to change HTML content based on
    the testing condition, you configure it here as well, overriding the default values in `CONFIGURATION`.
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
    DEV
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

    # The quality scales
    qualities = ['<b>overall quality</b> compared to the reference sound for each recording',]

    # Descriptions of the quality scales
    quality_explanations = ['<b>Overall quality</b> refers to overall quality of a recording based on how similar it is'
                            ' to the reference sound. For example, if a recording is very similar to the the reference,'
                            ' it should be given a high rating. However, if a recording is very different from the '
                            'reference sound (e.g. because of degradation or additional sounds), it should be given a low'
                            ' rating.',]

    # ---------------------------------------------------------------------------------------------
    # TRAINING EXAMPLES FOR PARTICIPANTS
    # These are the reference examples for the training examples
    # List entries must be dicts composed as {<reference_name>: <example_url>, ...}
    reference_example_dict = [{'Reference': url_for('static', filename='audio/exp00_target.wav'),},]

    # These are the quality examples.
    # List entries should be dicts composed as {<description>: <example_url>, ...}
    quality_example_dicts = [{'Low': [url_for('static', filename='audio/exp00_anchorArtif.wav'),
                                      url_for('static', filename='audio/exp00_anchorDistTarget.wav')],
                              'High': [url_for('static', filename='audio/exp00_target.wav'), ]},]

    for quality, quality_explanation, reference_example_dict, quality_example_dict in zip(qualities,
                                                                                          quality_explanations,
                                                                                          reference_example_dict,
                                                                                          quality_example_dicts, ):
        config = copy.deepcopy(CONFIGURATION)
        config['reference_example_dict'] = reference_example_dict
        config['quality_example_dict'] = quality_example_dict

        config['test_title'] = config['test_title'].replace('<quality>', quality)

        config['introduction_html'] = config['introduction_html'].replace('<quality>', quality)
        config['introduction_html'] = config['introduction_html'].replace('<quality_explanation>', quality_explanation)

        config['first_task_introduction_html'] = config['first_task_introduction_html'].replace('<quality>', quality)
        config['first_task_introduction_html'] = config['first_task_introduction_html'].replace('<quality_explanation>',
                                                                                                quality_explanation)

        config['training_instructions_html'] = config['training_instructions_html'].replace('<quality>',
                                                                                            quality)
        config['training_instructions_html'] = config['training_instructions_html'].replace('<quality_explanation>',
                                                                                            quality_explanation)

        config['evaluation_instructions_html'] = config['evaluation_instructions_html'].replace('<quality>',
                                                                                                quality)
        config['evaluation_instructions_html'] = config['evaluation_instructions_html'].replace('<quality_explanation>',
                                                                                                quality_explanation)

        test = models.Test(json.dumps(config))

        db.session.add(test)

    # save all tests
    db.session.commit()

    for test in models.Test.query.all():
        for j in range(1, num_audio_files + 1):
            # THE AUDIO STIMULUS FILES
            data = json.dumps({'reference_files': [('Reference', 'exp%02d_target.wav' % j),],
                               'stimulus_files': [('S1', 'exp%02d_target.wav' % j),
                                                  ('S2', 'exp%02d_anchorArtif.wav' % j),
                                                  ('S3', 'exp%02d_anchorDistTarget.wav' % j),
                                                  ('S4', 'exp%02d_test5.wav' % j),
                                                  ('S5', 'exp%02d_test6.wav' % j),
                                                  ('S6', 'exp%02d_test7.wav' % j),
                                                  ('S7', 'exp%02d_test8.wav' % j)]})
            c = models.Condition(test_id=test.id, data=data)
            db.session.add(c)
            db.session.commit()