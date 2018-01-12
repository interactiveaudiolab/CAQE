Running the Evaluation on Amazon's Mechanical Turk
==================================================

In order to collect data quickly, we recommend recruiting participants for your audio evaluation by posting HITs (Human Information Tasks) to `Amazon's Mechanical Turk <http://mechanicalturk.amazon.com>`_ (MTurk), which is a microtask labor market. On this platform it is recommended that you pay workers at least $6.00 / hr (see `MTurk Guidelines for Academic Requesters <http://wiki.wearedynamo.org/index.php/Guidelines_for_Academic_Requesters>`_). On top of that Amazon also takes a fee. This works out to be comparable to what you would pay participants in a lab study, but you can obtain your data much more quickly and with less effort.


Recruiting Participants
-----------------------
To recruit participants to evaluate our audio, we post assignments on Mechanical Turk. For each assignment, a participant will perform a single trial (the evaluations associated with one `condition` as defined in the config, e.g. one MUSHRA)

#. `Create an account on MTurk <https://requester.mturk.com/>`_

#. Create an Amazon AWS IAM user with AmazonMechanicalTurkFullAccess and put your this user's credentials into your ``secret_keys.py`` file (under ``CAQE/src/caqe``).

    #. Log into `Amazon AWS <http://aws.amazon.com>`_
    #. Click on `Identity & Access Management` under Amazon Web Services.
    #. Click on `Users` on the side-panel menu.
    #. Click on `Create New Users`
    #. Enter a name for your CAQE application and press `Create`.
    #. Click `Show User Security Credentials` and copy those keys into the ``secret_keys.py`` file that you generated earlier using ``generate_key_file.py``.
    #. Click on `Policies` on the side-panel menu.
    #. Check ``AmazonMechanicalTurkFullAccess``, click the ``Policy Actions`` button at the top, and click ``Attach``.
    #. Attach the policy to the user you just created.

#. Configure the MTurk variables in your config file. These are all variables that have the ``MTURK`` prefix. Use these variables to set your HIT's title, description, reward, etc. See :doc:`source/caqe.configuration` for more information.

#. Set `APP_MODE` to `PRODUCTION`::

    $ export APP_MODE=PRODUCTION

#. Set the ``SERVER_ADDRESS`` environment variable to your production server, e.g. ::

    $ export SERVER_ADDRESS=<your-caqe-app>.herokuapp.com

#. After your variables are configured, post your HIT to the MTurk sandbox for testing. With the ``--debug`` flag HITs are created without the worker qualification requirements so that you can test them in the sandbox. ::

    $ python turk_admin_cli.py --debug create-hits <num_hits>

#. Your HITs will now be viewable on the Mechanical Turk sandbox site. Visit http://workersandbox.mturk.com and search for the title you provided in your configuration. You can expire them with ``turk_admin_cli.py``: ::

    $ python turk_admin_cli.py expire-all-hits

#. Once you are ready to post your HITs to production Mechanical Turk Site, clear out your database. E.g., for Heroku: ::

    $ heroku run python src/create_db.py

   set the ``MTURK_HOST`` environment variable: ::

    $ export MTURK_HOST='mechanicalturk.amazonaws.com'

   and then again use ``turk_admin_cli.py`` to create HITs: ::

    $ python turk_admin_cli.py create-hits <num_hits>

#. You can view the progress of your evaluation at http://your-caqe-app.com/admin/stats

.. note:: If you need to end the HIT early (e.g. you made a mistake or you have enough data), you can `expire` the hits: ::

    $ python turk_admin_cli.py expire-all-hits

Paying Participants
-------------------
After a HIT is complete, you must pay participants in a timely manner. The ``MTURK_AUTO_APPROVAL_DELAY_IN_SECONDS`` config variable sets the auto-approval window. ``MTURK_AUTO_APPROVAL_DELAY_IN_SECONDS`` seconds after a participant submits a HIT, they will automatically be paid the reward of ``MTURK_REWARD`` in USD.

If you need to approve HIT assignments and pay participants before this amount of time passes, you can issue the following command:

    $ python turk_admin_cli.py approve-all-assignments

After HIT assignment have been approved you can bonus participants. If you are asking the participant to perform a hearing screening or survey on their first HIT assignment, you should pay them for that extra time in the form of a bonus. To assign a bonus for all completed first assignments. (Note the bonus amount is set by default by the ``MTURK_FIRST_HIT_BONUS`` config variable): ::

   $ python turk_admin_cli.py give-first-trial-bonus <bonus_amt>

.. note:: If you are using the ``general_mushra.cfg``, ``sourceseparation_mushra.cfg``, ``general_pairwise.cfg``, or  ``sourceseparation_pairwise.cfg``  configurations, workers are told in the description that they will receive this bonus. Therefore, make sure to either pay the bonus or change description and instructions in the configuration.

If you are performing a pairwise-comparison listening test, you can bonus participants based on their pairwise consistency. This is a good incentive for workers. (see ``python turk_admin_clip.y give-pairwise-consistency-bonus --help`` and the ``MTURK_MAX_CONSISTENCY_BONUS``, ``MTURK_MIN_CONSISTENCY_THRESHOLD_FOR_BONUS`` for more details)::

   $ python turk_admin_cli.py give-pairwise-consistency-bonus

.. note:: If you are using the ``general_pairwise.cfg`` or ``sourceseparation_pairwise.cfg`` configurations, workers are told in the description that they will receive this bonus. Therefore, make sure to either pay the bonus or change description and instructions in the configuration.

Once you have paid the workers and downloaded the data (see :doc:`data_analysis`), you can dispose of the HITs: ::

   $ python turk_admin_cli.py dispose-all-hits

