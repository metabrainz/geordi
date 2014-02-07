from .extract import extract_value, PathTraversalFailure
import logging
logger = logging.getLogger('geordi.data.mapping.rule')

def _none_or_index(*args, **kwargs):
    return kwargs.get('index', None)

def _no_op_arg(value, *args, **kwargs):
    return value

def _make_callable(value):
    if not callable(value):
        return lambda *args, **kwargs: value
    else:
        return value

class Rule:
    def __init__(self, source, destination, condition=True,
                       ordering=_none_or_index, node_destination=None,
                       link=None, transform=_no_op_arg):
        # source is an extraction path to use
        self.source = source
        # destination returns a simple path array for the destination
        self.destination = _make_callable(destination)
        # node_destination returns a node (or None, for "this one") the destination applies to
        self.node_destination = _make_callable(node_destination)
        # ordering returns an ordering key
        self.ordering = _make_callable(ordering)
        # condition is a function that returns True or False given rule, value, data inputs
        self.condition = _make_callable(condition)
        # link is a function that returns a link (by data item ID) or None
        self.link = _make_callable(link)
        # transform is a function that transforms the value, if needed
        self.transform = _make_callable(transform)

    def run(self, data):
        '''Runs the rule, producing an array of (node, destination, value, ordering, link) tuples'''
        extracted_values = extract_value(data, self.source)
        values = []
        for (choices, value) in extracted_values:
            if self.condition(value, data, **choices):
                node = self.node_destination(value, data, **choices)
                destination = self.destination(value, data, **choices)
                ordering = self.ordering(value, data, **choices)
                link = self.link(value, data, **choices)
                values.append((node, destination, self.transform(value, data, **choices), ordering, link))
        return values

    def test(self, data):
        '''Tests that the source field exists and matches any conditions and returns True or False'''
        still_ok = True
        try:
            values = extract_value(data, self.source)
        except PathTraversalFailure as failure:
            logger.info('Testing failed due to PathTraversalFailure: %s', failure)
            still_ok = False
        if still_ok:
            still_ok = False
            for (choices, value) in values:
                if self.condition(value, data, **choices):
                    still_ok = True
                    logger.info('Rule ok for %r, %r, %r', value, data, choices)
                    break
        return still_ok
