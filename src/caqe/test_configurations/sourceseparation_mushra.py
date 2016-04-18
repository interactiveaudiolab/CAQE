import copy
from flask import url_for

import caqe.test_configurations.general_mushra
from caqe.test_configurations.general_mushra import SERVER_NAME

# CONFIGURATION contains all of the configurable values for the test. For each condition
CONFIGURATION = copy.deepcopy(caqe.test_configurations.general_mushra.CONFIGURATION)
CONFIGURATION = dict(CONFIGURATION, **{
    # ---------------------------------------------------------------------------------------------
    # MECHANICAL TURK VARIABLES
    # Description of MTurk HIT
    'description': 'This listening test aims to rate the quality of a set of signals produced by '
                   'source separation systems. Source separation aims to extract the signal of a '
                   'target source from a mixture of several sound sources. The resulting signals may'
                   ' include several types of degradations compared to the clean target source, '
                   'including distortions of the target source, remaining sounds from other sources '
                   'and additional artificial noise. Note that while the maximum number assignments '
                   'a worker can do is 2, it\'s possible that fewer than 2 may be available to you. '
                   '**CHROME ONLY** **BONUS AVAILABLE**',

    # ---------------------------------------------------------------------------------------------
    # FRONT-END VARIABLES
    # The reference stimuli in the MUSHRA task
    'references': (('Target', 'The target source which we are trying to isolate.'),
                   ('Mixture', 'The mixture containing the target source and other sources.')),

    # The HTML content of the preview page. This will be the same for all conditions, regardless of test since
    # conditions are assigned on the fly (so we can have complete control over condition assignment).
    'preview_html':
        """
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
        """,

    # ---------------------------------------------------------------------------------------------
    # DEFAULT CONDITION AND TEST-SPECIFIC VARIABLES
    #   (These will be configured for each condition and saved in the database)
    # The HTML content of the introduction page the first time they do a task
    'first_task_introduction_html':
        """
        <p>A sound separation system aims to extract a clean recording of a single target sound
        (e.g. the vocalist) from a recording containing a mixture of several sounds
        (e.g. the rest of the band). This listening test aims to rate the quality of
        recordings produced by different sound separation systems. Due to imperfections of each
        sound separation system, the output recording (e.g. vocals extracted from the
        mixture) may include several types of degradations compared to the clean target
        sound&mdash;it might be a little distorted, you still might be able to hear the background
        (a little or a lot), it might have strange artifacts.</p>

        <p>During the test, you will be asked to rate the <quality>. The test will have three
        parts: 1) a short hearing test phase, 2) a training phase and 3) an evaluation
        phase. During the training phase, you will have to listen to all the recordings to
        train yourself to notice the <quality> and learn the range of quality that is possible.
        During the evaluation phase, you will have to rate the quality of eight test recordings
        compared to the perfect target sound. Lastly, at the end, there will be a short survey
        which you will only have to fill out for the first HIT you complete.</p>

        <p>Including the survey at the end, the expected total duration of the first HIT is 8
        minutes. Because this first HIT takes longer than the rest of the HITs in this group,
        you will be given a $0.30 bonus.</p>
        """,

    # The HTML content of the introduction page (after the first time they perform the task)
    'introduction_html':
        """
        <p>A sound separation system aims to extract a clean recording of a single target sound
        (e.g. the vocalist) from a recording containing a mixture of several sounds
        (e.g. the rest of the band). This listening test aims to rate the quality of
        recordings produced by different sound separation systems. Due to imperfections of each
        sound separation system, the output recording (e.g. vocals extracted from the
        mixture) may include several types of degradations compared to the clean target
        sound&mdash;it might be a little distorted, you still might be able to hear the background
        (a little or a lot), it might have strange artifacts.</p>

        <p>During the test, you will be asked to rate the <quality>. The test will have three
        parts: 1) a short hearing test phase, 2) a training phase and 3) an evaluation
        phase. During the training phase, you will have to listen to all the recordings to
        train yourself to notice the <quality> and learn the range of quality that is possible.
        During the evaluation phase, you will have to rate the quality of eight test recordings
        compared to the perfect target sound.</p>

        <p>The expected total duration of the test is 5 minutes.</p>
        """,
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
    qualities = ['<b>overall quality</b> compared to the target sound for each recording',
                 'quality in terms of <b>preservation of the target sound</b> in each recording',
                 'quality in terms of <b>suppression of other sounds</b> in each recording',
                 'quality in terms of <b>absence of additional artificial noise</b> in each recording',
                 'quality in terms of <b>lack of distortions to the target sound</b> in each recording']

    # Descriptions of the quality scales
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

    # ---------------------------------------------------------------------------------------------
    # TRAINING EXAMPLES FOR PARTICIPANTS
    # These are the reference examples for the training examples
    # List entries must be dicts composed as {<reference_name>: <example_url>, ...}
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

    #
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