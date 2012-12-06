# ingestr-server
# Copyright (C) 2012 Ian McEwen, MetaBrainz Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import

import re

def comma_list(lst):
    if len(lst) > 1:
        return ", ".join(lst[:-1]) + " and " + lst[-1]
    else:
        return lst[0]

def collect_text(block, regex='.*'):
    try:
        text = block['text']
        if re.search(regex, text):
            return [text]
        else:
            return []
    except KeyError:
        return []
    except TypeError:
        return [entry['text'] for entry in block if ('text' in entry and re.search(regex, entry['text']))]

def use_first_text(block, regex='.*'):
    return collect_text(block, regex)[0]

def alternate_text(block, regex='.*'):
    return collect_text(block, regex)[1:]

def concatenate_text(block, regex='.*', combiner=comma_list):
    return combiner(collect_text(block, regex))

def base_mapping():
    return {
        'release': {
            'title': None,
            'alternate_titles': [],
            'date': None,
            'artist': [],
            'combined_artist': None
        }
    }
