Downloading and Analyzing Data
==============================

Downloading and restoring database from Heroku
-----------------------------------------------
#. Create a psql user if you haven't already: ::

	$ sudo -u postgres createuser -P <local-username>

#. Create a local database owned by that user: ::

	$ sudo -u postgres createdb -O <local-username> <dbname>

#. Capture a database snapshot on Heroku: ::

    $ heroku pg:backups capture

#. Download the snapshot from Heroku to your local machine: ::

    $ curl -o latest.dump `heroku pg:backups public-url`

#. Restore database on local machine: ::

    $ pg_restore --verbose --clean --no-acl --no-owner -h localhost -U <local-username> -d <dbname> latest.dump

#. Configure your local CAQE app to use the database. This can achieved either by setting the ``SQLALCHEMY_DATABASE_URI`` in the CAQE configuration (see :doc:`source/caqe.configuration`) or by setting the ``DATABASE_URL`` environment variable, e.g ::

	$ export DATABASE_URL='postgres://<local-username>:<psql-password>@localhost/<dbname>'


MUSHRA Analysis
---------------
First make sure that you have all of the required Python packages for analysis These are not included in the main ``requirements.txt`` file because they are not needed for deployment. ::

    $ pip install -r analysis_requirements.txt


To access and format the results of a MUSHRA listening test, either use the ``analysis.py`` module: ::

    >> import analysis
    >> data = analysis.get_ratings_data()

or export the data to a CSV using the CLI command: ::

    $ python analysis.py save-data-to-csv <output_file.csv>


To plot the results of a MUSHRA listening test, either use the ``analysis.py`` module ::

    >> import analysis
    >> import matplotlib.pyplot as plt
    >> data = analysis.get_ratings_data()
    >> analysis.plot_mushra_boxplots(data)
    >> plt.show()

or export the plot to a image file (e.g. a ``.png``, ``.pdf``, etc.) using the CLI command: ::

    $ python analysis.py plot-mushra-boxplots <output_file.pdf>


