Development
===========
The following installation instructions are for Ubuntu.

#. Install dependencies if they are not already installed. (for platforms other than Ubuntu, follow the `installation instructions <https://pip.pypa.io/en/stable/installing/>`_)::

    $ sudo apt-get install git python-pip python-dev postgresql postgresql-server-dev-all

#. Clone or download the CAQE repository from Github: http://github.com/mcartwright/CAQE , e.g. ::

    $ git clone https://github.com/mcartwright/CAQE.git
    $ cd CAQE

#. (*optional*) Install ``virtualenv`` (if not installed already) and create a ``caqe`` virtual environment ::

    $ sudo pip install virtualenv
    $ virtualenv ~/Envs/caqe
    $ source ~/Envs/caqe/bin/activate

#. Install the python module dependencies in ``requirements.txt`` using ``pip``.::

    $ pip install -r requirements.txt

#. Configure testing variables as described in :doc:`test_configurations`.
#. Set `APP_MODE` to `DEVELOPMENT`::

    $ export APP_MODE=DEVELOPMENT

#. Generate `secret_keys.py` (don't check this file into source control)::

    $ cd src
    $ python generate_key_file.py

#. Create the database::

    $ python create_db.py

#. Add ``0.0.0.0     caqe.local`` to a new line in your ``/etc/hosts`` file.

#. Start the development server::

    $ python run.py

#. Go to http://caqe.local:5000/mturk_debug to test the configuration.

#. Stop the server with ``ctrl-c``.