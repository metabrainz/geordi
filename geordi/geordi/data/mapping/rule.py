from .extract import extract_value, PathTraversalFailure
from .pathutils import make_callable, no_op_value
import logging
logger = logging.getLogger('geordi.data.mapping.rule')

class Rule:
    def __init__(self, source, destination, condition=True, node_destination=None,
                       link=None, link_only=False, transform=no_op_value):
        # source is an extraction path to use
        self.source = source
        # destination returns a simple path array for the destination
        self.destination = make_callable(destination)
        # node_destination returns a node (or None, for "this one") the destination applies to
        self.node_destination = make_callable(node_destination)
        # condition is a function that returns True or False given rule, value, data inputs
        self.condition = make_callable(condition)
        # link is a function that returns a link (by data item ID) or None, with type derived from destination
        self.link = make_callable(link)
        self.link_only = make_callable(link_only)
        # transform is a function that transforms the value, if needed
        self.transform = make_callable(transform)

    def run(self, data):
        '''Runs the rule, producing an array of (node, destination, value, link) tuples'''
        extracted_values = extract_value(data, self.source)
        values = []
        for (choices, value) in extracted_values:
            if self.condition(value, data, **choices):
                node = self.node_destination(value, data, **choices)
                destination = self.destination(value, data, **choices)
                link = self.link(value, data, **choices)
                if self.link_only(value, data, **choices):
                    value = None
                else:
                    value = self.transform(value, data, **choices)
                values.append((node, destination, value, link))
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
