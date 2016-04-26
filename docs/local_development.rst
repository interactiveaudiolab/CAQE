Local Development
=================
The following installation instructions are for Ubuntu.

#. Clone or download the CAQE repository from Github: http://github.com/mcartwright/CAQE , e.g. ::

    $ git clone https://github.com/mcartwright/CAQE.git
    $ cd CAQE

#. Install ``pip`` it if is not already installed. (for platforms other than Ubuntu, follow the `installation instructions <https://pip.pypa.io/en/stable/installing/>`_)::

    $ sudo apt-get install python-pip

#. (*optional*) Create a ``caqe`` virtual environment (if ``virtualenvwrapper`` is not installed, follow the `installation instructions <https://virtualenvwrapper.readthedocs.org/en/latest/>`_) ::

    $ mkvirtualenv caqe

#. Install the dependencies in ``requirements.txt`` using ``pip``.::

    $ sudo apt-get install python-dev
    $ pip install -r requirements.txt

#. `Configure testing variables <test_configurations.html>`_.
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