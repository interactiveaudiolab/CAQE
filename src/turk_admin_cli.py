#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command-line utility for accessing the functions in caqe.turk_admin
"""
import argparse
import caqe.turk_admin
from caqe import app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage the Amazon Mechanical Turk assignments and workers for CAQE.')
    sp = parser.add_subparsers(dest='command')

    ch = sp.add_parser('create-hits', help='Create MTurk HITs')
    ch.add_argument('num_hits', type=int, help='The number of MTurk HITs to create')

    eah = sp.add_parser('expire-all-hits', help='Expire all MTurk HITs')

    dah = sp.add_parser('dispose-all-hits', help='Dispose of all MTurk HITs')

    aas = sp.add_parser('approve-all-assignments', help='Approve all assignments and pay the assignment reward.')

    gftb = sp.add_parser('give-first-trial-bonus', help='Give a bonus to all workers that completed their first trial, '
                                                        'which may have had additional testing.')
    gftb.add_argument('reward',
                      type=float,
                      help="The default bonus reward in USD that is optionally given (using ``turk_admin_cli.py``) to "
                           "participants tha completed the first assignment, which may have additional testing (e.g. "
                           "survey, hearing tests, etc.)",
                      nargs="?",
                      default=app.config['MTURK_FIRST_HIT_BONUS'])
    gftb.add_argument('--display-only',
                      help="Do not actually pay out the bonus. Just calculate and display the total.",
                      action='store_true')

    gpcb = sp.add_parser('give-pairwise-consistency-bonus', help='Give a bonus to workers based on their pairwise '
                                                                 'consistency.')
    gpcb.add_argument('max-consistency-bonus',
                      type=float,
                      help="The default maximum bonus reward in USD for pairwise consistency.",
                      nargs="?",
                      default=app.config['MTURK_MAX_CONSISTENCY_BONUS'])
    gpcb.add_argument('min-consistency-threshold-for-bonus',
                      type=float,
                      help="The minimum pairwise consistency required to receive the optional bonus (given through "
                           "``turk_admin_cli.py``.",
                      nargs="?",
                      default=app.config['MTURK_MIN_CONSISTENCY_THRESHOLD_FOR_BONUS'])
    gpcb.add_argument('--display-only',
                      help="Do not actually pay out the bonus. Just calculate and display the total.",
                      action='store_true')

    args = parser.parse_args()

    turk_admin = caqe.turk_admin.TurkAdmin()

    if args.command == 'create-hits':
        turk_admin.create_hits(args.num_hits)
    elif args.command == 'expire-all-hits':
        turk_admin.expire_all_hits()
    elif args.command == 'dispose-all-hits':
        turk_admin.dispose_all_hits()
    elif args.command == 'approve-all-assignments':
        turk_admin.approve_all()
    elif args.command == 'give-first-trial-bonus':
        a = vars(args)
        turk_admin.give_bonus_to_all_first_completed_trials(a['reward'],
                                                            a['calculate-amt-only'])
    elif args.command == 'give-pairwise-consistency-bonus':
        a = vars(args)
        turk_admin.give_consistency_bonus(a['max-consistency-bonus'],
                                          a['min-consistency-threshold-for-bonus'],
                                          a['display-only'])


