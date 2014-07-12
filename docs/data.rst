Geordi data structure
=====================

This document will provide a short conceptual overview of the various objects that make up Geordi, and their relations.

Geordi objects
--------------

Item
^^^^
The core object of geordi is the 'item'. This is geordi's overarching container for entities of all sorts: releases, artists, labels, places, areas, whatever. Items have an *id*, a nominal *type* (roughly: "we think this is a release" or "we think this is an artist"), and a *map* -- that is, data in a standard format defining the entity. 

Data Item
^^^^^^^^^
Conceptually contained by items are what I'll call "data items": a bit of data from a specific source with a specific identifier relative to that source. This includes chunks of data derived from broader items, for example in a data source that only provides data files for releases, it is still often possible to extract information identifying and describing an artist, or a recording. Data items have an *id* composed of a data source (called 'index'), an item type, and an identifier (perhaps an integer, perhaps a catalog number, perhaps just a name -- depends on the source), a link to an item, and the data itself.

Upon initial insertion to geordi, each item contains exactly one data item. Eventually it should be possible to merge items together (or, perhaps more accurately, match items within geordi to each other -- for example, the same artist as represented in two different data sources). Data items cannot be directly linked to anything except items, since items represent the links between data items other than equivalence. However, data items carry most of the actual data in geordi, so many things are derived from them.

Editor
^^^^^^
The third basic object that doesn't represent some sort of relation is an editor. Editors represent both human users who log in via MB and automatic processes indigenous to geordi.

Geordi relations
----------------

Item Links
^^^^^^^^^^
Aside from the mapped data, another thing that can be extracted from data items is connections between pieces of data within a dataset. For example, a dataset with identifiers for both release and recording objects will probably include a list of references to recordings in its data for the release. Upon mapping, these are extracted into item links in geordi. Item links are composed of an item being linked from, a linked item (the other end of the link), and a type. The type is written as a path into the item's mapped data, separated by '%' characters, for example a type of release%artists%split%names%1 for the second artist listed at the release level.

Raw Matches
^^^^^^^^^^^
More complicated, but rather important, are links to entities within MusicBrainz. These present a lot of complication for the simple reason that they can often be represented, in various ways, from both geordi and from MusicBrainz. To simplify things somewhat, I'll first talk about *raw matches*: matches stored within geordi, that have no equivalent inverse way to be stored in MusicBrainz (perhaps a dataset derived from a private site that can't be linked to with URL relationships). These consist of an item, a set of mbid + type pairs, a user, and a timestamp. For the sake of storing history, raw matches can also be marked as 'superseded', when a new match is registered instead.

MusicBrainz Matches
^^^^^^^^^^^^^^^^^^^
(Note: not yet implemented). For data sources where relationships within MusicBrainz itself are present, it would be best not to duplicate that information and potentially let it get out of sync. So, ultimately, geordi should also be able to pull matches from MusicBrainz's data. This would presumably be done by way of either including a replicated MusicBrainz database alongside geordi, which it can then query, or as some sort of materialization process.

Automatic Matching
^^^^^^^^^^^^^^^^^^
(Note: not yet implemented). Matches of various sorts may be suggested or created by automated process indigenous to geordi; for example, if a release is already matched to MusicBrainz and has only one artist in both databases, it's relatively likely the two artists are the same. Matches created by such a process are referred to as automatic matches.

Technical details
-----------------

Geordi's data is stored in a PostgreSQL database. Further details of the schema and interconnections are documented in the :doc:`db` document, or can be investigated by reading the SQLAlchemy model definitions or creating a geordi database and using PostgreSQL's built-in introspection tools.
