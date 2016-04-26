Test Configurations
===================
Before running a CAQE test, the configuration variables must be set. These variables define the stimuli, \
quality scales, Mechanical Turk variables, instructions, etc.

The CAQE configuration variables are set in three stages:

**Stage 1:** The base configuration is set as defined in :py:class:`caqe.configuration.BaseConfig`

**Stage 2:** CAQE reads in the configuration file whose path is set by the environment variables ``CAQE_CONFIG``. \
Any uppercase variables (e.g. ``TEST_TYPE='mushra'``) in the file will be added to the configuration (and override any \
existing variables of the same name). If the ``CAQE_CONFIG`` variable is not set, then by default CAQE will read in \
the :ref:`general-mushra-label` configuration.

**Stage 3:** Lastly, another environment variable, ``APP_MODE``, may be set to override configuration variables for \
development, testing, or production. See :py:class:`caqe.configuration.DevelopmentOverrideConfig`, \
:py:class:`caqe.configuration.TestingOverrideConfig`, and :py:class:`caqe.configuration.ProductionOverrideConfig`.

Therefore, to configure your test, use a pre-defined configuration as a guide to make your own configuration file, and \
then set the environment variable to the files location. The location should either be an absolutely path or \
a path relative to ``caqe.__init__.py``. For example: ::

    $ export CAQE_CONFIG='/home/your_username/your_caqe_config.cfg'

.. seealso:: :doc:`/source/caqe.configuration` for more information on the configuration variables.


General Overall Quality Test Configurations
-------------------------------------------

.. _general-mushra-label:

General MUSHRA
^^^^^^^^^^^^^^
File: ``general_mushra.cfg``

A general MUSHRA (MUltiple Stimulus Hidden Reference and Anchor) configuration for evaluating overall quality
of a set of audio stimuli.

To activate: ::

    $ export CAQE_CONFIG='../test_configurations/general_mushra.cfg'

General Pairwise
^^^^^^^^^^^^^^^^
File: ``general_pairwise.cfg``

A general pairwise (e.g. A is better than B) configuration for evaluating overall quality
of a set of audio stimuli.

To activate: ::

    $ export CAQE_CONFIG='../test_configurations/general_pairwise.cfg'

Source Separation Test Configurations
-------------------------------------

Source Separation MUSHRA
^^^^^^^^^^^^^^^^^^^^^^^^
File: ``sourceseparation_mushra.cfg``

A MUSHRA (MUltiple Stimulus Hidden Reference and Anchor) configuration for evaluating output quality of audio source
separation algorithms on 4 different quality scales:

#. Preservation of the Target Sound
#. Suppression of Other Sounds
#. Absence of Additional Artificial Noise
#. Lack of Distortions to the Target Sound

To activate: ::

    $ export CAQE_CONFIG='../test_configurations/sourceseparation_mushra.cfg'

Source Separation Pairwise
^^^^^^^^^^^^^^^^^^^^^^^^^^
File: ``sourceseparation_pairwise.cfg``

A pairwise (e.g. A is better than B configuration for evaluating output quality of audio source
separation algorithms on 4 different quality scales:

#. Preservation of the Target Sound
#. Suppression of Other Sounds
#. Absence of Additional Artificial Noise
#. Lack of Distortions to the Target Sound

To activate: ::

    $ export CAQE_CONFIG='../test_configurations/sourceseparation_pairwise.cfg'

