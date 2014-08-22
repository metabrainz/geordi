geordi
======

This project allows the consumption of arbitrary data, for use as a data source and matching tool.

![Geordi La Forge](http://images1.wikia.nocookie.net/__cb20120205164005/memoryalpha/en/images/thumb/d/d9/Geordi_La_Forge_2368.jpg/158px-Geordi_La_Forge_2368.jpg)

It's named after [Geordi La Forge](http://en.memory-alpha.org/wiki/Geordi_La_Forge), in reference to [MusicBrainz Picard](https://github.com/musicbrainz/picard).

Setup
-----

### Shared dependencies:

* postgresql

You will also need to be able to install python packages, we recommend
using virtualenvwrapper for this.  On Debian/Ubuntu systems you can
install that with:

    sudo apt-get install virtualenvwrapper

### Python dependencies:

    mkvirtualenv geordi

The mkvirtualenv command will create and activate a virtual
environment in which python modules will be installed.  You can
re-active this environment with the following command:

    workon geordi

To install all the dependencies run:

    pip install -r requirements.txt

### Configuration

In the geordi/geordi directory, copy settings.cfg.sample to settings.cfg;
modify database connection settings, set MusicBrainz OAuth configuration,
and make any other needed changes.

### Creating database

To create a database matching the default configuration run:

    createdb -O geordi geordi

Then create the schema by running:

    echo 'CREATE SCHEMA geordi' | psql -U geordi geordi

### Creating tables

To create tables in an existing database run:

    python manager.py create_tables

*(replace 'python' with 'python2' where applicable)*

Importing Data
--------------

To import data, use the manager.py script in the 'geordi' directory. Various
options exist under the 'data' subcommand, for which documentation exists.
Source-specific import tools are in the geordi.data.importer module, mostly
under the 'indexes' subdirectory.

Running server
--------------

To run the server:

    cd geordi
    python manager.py runserver

*(replace 'python' with 'python2' where applicable)*


Testing
-------

To run tests, install nose (remember to enable your virtualenv!):

    pip install nose

And then run the tests, you should see something like this:

    $ nosetests
    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.121s
    
    OK


Further Documentation
---------------------

The geordi server has some [additional documentation](https://geordi.readthedocs.org/) as well.
