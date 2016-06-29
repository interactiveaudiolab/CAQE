#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analysis module for estimating scores for performing statistical tests.

Run on the command line, e.g.: ::

    $ python analysis.py

.. note:: This module has dependencies not required by the CAQE web application. To install these dependencies, run ``pip install -r analysis_requirements.txt``.
"""
import argparse
import copy
import json

import pandas as pd
import seaborn as sns

from caqe.models import Condition
from caqe import app


def get_ratings_data(output_file=None):
    """
    Get the ratings data from the database as a DataFrame

    Parameters
    ----------
    output_file : str
        A filepath to an output CSV file (default is None)

    Returns
    -------
    ratings : pandas.DataFrame
        All of the rating data from the dictionary.

    """
    conditions = Condition.query.all()
    ratings = []
    for c in conditions:
        for t in c.trials.all():
            t_data = json.loads(t.data)
            trial_ratings = t_data['ratings']
            del t_data['ratings']
            row = {'test_id': c.test_id,
                   'trial_id': t.id,
                   'condition_id': c.id,
                   'participant_id': t.participant_id,
                   'participant_crowd_worker_id': t.participant.crowd_worker_id,
                   'participant_platform': t.participant.platform,
                   'participant_passed_hearing_test': t.participant_passed_hearing_test,
                   'participant_hearing_test_attempts': t.participant.hearing_test_attempts,
                   'participant_hearing_test_last_attempt': t.participant.hearing_test_last_attempt,
                   'participant_pre_test_survey': t.participant.pre_test_survey,
                   'participant_post_test_survey': t.participant.post_test_survey,
                   'participant_hearing_response_estimation': t.participant.hearing_response_estimation,
                   'data': json.dumps(t_data)}
            for k, v in trial_ratings.items():
                r = copy.deepcopy(row)
                r['stimulus'] = k
                r['rating'] = float(v)
                ratings.append(r)

    ratings = pd.DataFrame.from_records(ratings)

    if output_file is not None:
        ratings.to_csv(output_file)

    return ratings


def plot_mushra_boxplots(data, size=5, output_file=None):
    """
    Plot the MUSHRA ratings as a grid of boxplots. If `output_file` is defined, then save the plot to file.

    Parameters
    ----------
    data: pandas.DataFrame
        The ratings data obtained from `get_ratings_data`.

    size : float
        Height of each boxplot in inches. (default is 5)

    output_file: str
        Path to the output file location. (default is None)

    Returns
    -------
    g : seaborn.axisgrid.FacetGrid
    """
    g = sns.factorplot(x='stimulus', y='rating', data=data, row='condition_id', kind='box', notch=True, size=size)
    g.set(ylim=(app.config['MIN_RATING_VALUE'], app.config['MAX_RATING_VALUE']))

    if output_file is not None:
        g.savefig(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze and plot CAQE results.')
    sp = parser.add_subparsers(dest='command')

    ch = sp.add_parser('plot-mushra-boxplots', help='Plot the MUSHRA ratings as a grid of boxplots.')
    ch.add_argument('output_file', type=str, help='Path to output file location')
    ch.add_argument('--size', type=float, help='Height of each boxplot in inches.', default=5.)

    ch = sp.add_parser('save-data-to-csv', help='Save MUSHRA data to a csv file.')
    ch.add_argument('output_file', type=str, help='Path to output file location')

    args = parser.parse_args()

    if args.command == 'plot-mushra-boxplots':
        data = get_ratings_data()
        plot_mushra_boxplots(data, size=args.size, output_file=args.output_file)
    elif args.command == 'save-data-to-csv':
        get_ratings_data(args.output_file)

