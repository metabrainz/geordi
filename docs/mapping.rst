Mapping
=======

Mapping in geordi is done by way of an array of rule definitions, looked up by the data source name (i.e. index name) and item type (for example, ninjatune/release, or test_index/artist). The rules are within geordi/data/mapping/indexes/, in a file by index name, which exports a dictionary mapping item type to a list of rules.

The rule language is defined by a set of other files within geordi/data/mapping, especially geordi/data/mapping/rule.py and geordi/data/mapping/extract.py; in general, rules specify a path within the source data (potentially including some choices to be made by the extractor, e.g. to continue within every element of an array, or to continue along some keys of a dictionary but not others) and a destination path to which the data should be mapped. Though there are defaults, rules are generally expected to provide a condition (i.e., which values to accept, defaulting to all) and an ordering value (i.e., where in the result array to put the value, defaulting to None to specify the order doesn't matter).

Rules are also permitted to provide information about links (to other data items; the types of these links will be determined by the destination path of the rule), a function to transform the data before insertion, and may specify a node to which the destination applies (defaulting to "the node corresponding to the data item being mapped"; this functionality is to be used when an index provides information about linked entities within the data for another entity, but does not provide separate information about the linked entity, e.g. provides artist type information in a release listing).

For more information, it's recommended to look at the various indexes' mapping rules.

Weaknesses
----------

* It's not currently possible to have a rule depend on multiple locations in the source data -- while choices can be made, if e.g. it's possible for the index to provide more than one track title and more than one track title version for each track, a cross product can't be generated to e.g. have the track name suggestions be ["title 1 (version 1)", "title 2 (version 1)", "title 1 (version 2)", "title 2 (version 2)"]. This could be fixed by making it possible for rules to generate multiple values, and using a 'transform' function at a higher level in the tree.
