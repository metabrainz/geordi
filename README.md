geordi
-------

This project allows the consumption of arbitrary data, for use as a data source and matching tool.

![Geordi La Forge](http://images1.wikia.nocookie.net/__cb20120205164005/memoryalpha/en/images/thumb/d/d9/Geordi_La_Forge_2368.jpg/158px-Geordi_La_Forge_2368.jpg)

It's named after [Geordi La Forge](http://en.memory-alpha.org/wiki/Geordi_La_Forge), in reference to [MusicBrainz Picard](https://github.com/musicbrainz/picard).

Setup
=====

Shared dependencies: elasticsearch -- install and make available,
presumably on localhost:9200 (the default).  See
http://www.elasticsearch.org/download/ .

You will also need to be able to install python packages, we recommend
using virtualenvwrapper for this.  On Debian/Ubuntu systems you can
install that with:

`sudo apt-get install virtualenvwrapper`

----

Python dependencies:

`mkvirtualenv geordi`

The mkvirtualenv command will create and activate a virtual
environment in which python modules will be installed.  You can
re-active this environment with the following command:

`workon geordi`

To install all the dependencies run:

`pip install -r requirements.txt`

----

To run the server:

`python geordi/run.py`

----

For importing, perl dependencies:

`cpanm XML::XML2JSON LWP::UserAgent HTTP::Request URI::Escape Encode JSON Try::Tiny File::Slurp`

----

To import data, from tools directory:

`./submit-dir.pl --index some-index-name /some/directory/*`

Where * should be a bunch of directories named by identifier, containing XML and JSON files.

Usage
=====

Thus far, only displays data, updates when that's fixed!


Tests
=====

To run tests, install nose:

`./geordi/bin/pip install nose`

And then run the tests, you should see something like this:

    $ ./geordi/bin/nosetests
    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.121s
    
    OK


Code Layout
===========

geordi subdir: new python codebase (GPLv3+)

tools subdir:

 * submit-dir.pl

    Submits files to the local elastic search server.

 * other largely outdated files for historical understanding

ingestr-server-perl subdir: old perl codebase
