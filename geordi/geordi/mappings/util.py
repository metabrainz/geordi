# geordi
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

from __future__ import division, absolute_import, unicode_literals

import re

def comma_list(lst):
    if len(lst) == 0:
        return ''
    elif len(lst) == 1:
        return lst[0]
    else:
        return ", ".join([unicode(i) for i in lst[:-1]]) + " and " + unicode(lst[-1])

def comma_only_list(lst):
    return ", ".join(lst)

def collect_text(block, regex='.*'):
    if block is None:
        return []
    try:
        text = unicode(block['text'])
        if re.search(regex, text):
            return [text]
        else:
            return []
    except KeyError:
        return []
    except TypeError:
        return [unicode(entry['text']) for entry in block if (entry and 'text' in entry and re.search(regex, entry['text']))]

def concatenate_text(block, regex='.*', combiner=comma_list):
    return combiner(collect_text(block, regex))

def base_mapping():
    return {
        'release': {
            'title': [],
            'date': [],
            'artist': [],
            'label': [],
            'catalog_number': [],
            'combined_artist': '',
            'tracks': []
        }
    }

def format_track_length(ms):
    if ms is None:
        return '?:??'
    elif ms < 1000:
        return '{} ms'.format(ms)
    elif ms < 3600000:
        sec = (ms + 500) // 1000
        return '{}:{:02d}'.format(sec // 60, sec % 60)
    else:
        sec = (ms + 500) // 1000
        return '{}:{:02d}:{:02d}'.format(sec // (60 * 60), (sec % (60 * 60)) // 60 , sec % 60)
