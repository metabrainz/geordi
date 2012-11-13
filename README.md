== ingestr ==

This project allows the consumption of arbitrary data, for use as a data source and matching tool.

=== Setup ===

Shared dependencies: elasticsearch -- install and make available, presumably on localhost:9200 (the default)

----

Python dependencies:
virtualenv some-dir
./some-dir/bin/pip install Flask

----

To run the server, from ingestr-server directory:
/virtualenv/dir/bin/python ingestr.py

----

For importing, perl dependencies:
cpanm XML::XML2JSON LWP::UserAgent HTTP::Request URI::Escape Encode JSON Try::Tiny File::Slurp

----

To import data, from tools directory:

./submit-dir.pl --index some-index-name /some/directory/\*

Where \* should be a bunch of directories named by identifier, containing XML and JSON files.

=== Usage ===

Thus far, only displays data, updates when that's fixed!

=== Code Layout ===

ingestr-server subdir:
   new python codebase
tools subdir:
   submit-dir.pl
      Submits files to the local elastic search server
      Requires: XML::XML2JSON LWP::UserAgent HTTP::Request URI::Escape Encode JSON Try::Tiny File::Slurp
   other largely outdated files for historical understanding
ingestr-server-perl subdir:
   old perl codebase
