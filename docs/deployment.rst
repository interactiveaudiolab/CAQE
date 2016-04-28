Deployment
==========


Deploying on Heroku
-------------------
`Heroku <http://www.heroku.com>`_ is a cloud hosting service. This enables you to deploy a web app to a server without having a server of your \
own or knowing much about server administration. After you have a Heroku account and the local Heroku tools installed, \
deployment is as simple as pushing a Git repository to Heroku and setting a few environment variables.

Steps for deployment are as follows:

#. If you haven't already, follow the instructions :doc:`development` to download and configure CAQE.

#. `Sign up for a Heroku account <https://signup.heroku.com/dc>`_

#. `Download the Heroku Toolbelt <https://toolbelt.heroku.com/debian>`_ ::

    $ wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh

#. Login to Heroku using your credentials: ::

    $ heroku login

#. **While in the root directory of your CAQE repository**, link the repository with Heroku by running the following command, changing the optional ``<your-caqe-app>`` parameter to your desired subdomain (without this parameter, a random subdomain is generated.): ::

    $ heroku create <your-caqe-app>

#. After running the command, make note of the server address.
#. Make sure your audio stimulus files are in the ``src/caqe/static/audio`` directory and your configuration file is in ``test_configurations``. Add the files to your git repository and commit the changes, e.g.: ::

    $ git add .
    $ git commit -m 'Configured CAQE for comparing the output of Robust PCA and REPET'

#. Push your repository to Heroku. ::

    $ git push heroku master

#. Set your secret key environment variables. You can set the environment variables in Heroku with the ``heroku config:set`` command. Use this command to set environment variables to the secret keys in ``secret_keys.py`` (generated from ``generate_key_file.py``): ::

    $ heroku config:set SESSION_KEY='DcE34cFEDEB37131df97EeF5BB56AfCF'
    $ heroku config:set CSRF_SECRET_KEY='E7a1989EbaaeF60cEab4Cb9534851e42'

#. Then set your configuration variables, specifying your config filename and the server address, e.g.: ::

    $ heroku config:set CAQE_CONFIG='<your-caqe-config>.cfg'
    $ heroku config:set APP_MODE='PRODUCTION'
    $ heroku config:set SERVER_ADDRESS='<your-caqe-app>.herokuapp.com'

#. Now that our variables are set. Let's set and create the database. First we have to enable Postgresql on Heroku. `There are a number of different plans <https://devcenter.heroku.com/articles/heroku-postgres-plans>`_, but most likely the `heroku-dev` plan will be enough for us: ::

    $ heroku addons:create heroku-postgresql:hobby-dev

#. Double check the command completed. If it did, the following command will not have output: ::

    $ heroku pg:wait

#. Create and initialize the database. ::

    $ heroku run python src/create_db.py

#. Now, ensure that at least one instance of the app is running: ::

    $ heroku ps:scale web=1

   .. note:: Though when you actually start collecting data with your CAQE app, we recommend increasing the number of instances to at least 2.

#. To test how your evaluation will appear to a Mechanical Turk worker, go to http://your-caqe-app.herokuapp.com/mturk_debug

.. seealso:: `Getting Started on Heroku with Python <https://devcenter.heroku.com/articles/getting-started-with-python#introduction>`_