#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A test configuration defines the user-tunable parameters of the quality evaluation such as the:

* Amazon Mechanical Turk HIT description, pricing, keywords, etc.
* The description and instructions of the task
* The configuration of the type of test (e.g 'mushra' or 'pairwise')
* The definition of the quality scales
* The paths to the audio stimuli
* Which components of the evaluation are active (e.g. pre-test survey, post-test survey, hearing screening, etc.)

This subpackage contains a base configuration which contains overridable defaults, as well as pre-defined testing
configurations for common audio quality evaluation scenarios.
"""