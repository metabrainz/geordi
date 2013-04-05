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
import collections

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
    match = re.compile(regex)
    if block is None:
        return []
    try:
        text = unicode(block['text'])
        if match.search(text):
            return [text]
        else:
            return []
    except KeyError:
        return []
    except TypeError:
        return [unicode(entry['text']) for entry in block if (entry and 'text' in entry and match.search(entry['text']))]

def concatenate_text(block, regex='.*', combiner=comma_list):
    return combiner(collect_text(block, regex))

def collect_obj(block, path_filter=None):
    if block is None:
        blocks = []
    if isinstance(block, collections.Mapping):
        blocks = [block]
    elif isinstance(block, collections.Iterable):
        blocks = block
    else:
        blocks = []
    if path_filter is None:
        return blocks
    else:
        final = []
        for entry in blocks:
            append = False
            for (path, value) in path_filter.iteritems():
                try:
                    path_keys = path.split('.')
                    dest = entry
                    for key in path_keys:
                        dest = dest[key]
                    if re.search(value, dest):
                        append = True
                    else:
                        append = False
                        break
                except:
                    append = False
                    break
            if append:
                final.append(entry)
        return final

def base_mapping(maptype):
    mapping = {'version': 0}
    if maptype == 'release':
        mapping.update({
            'release': {
                'title': [],
                'date': [],
                'country': [],
                'artist': [],
                'other_artist': [],
                'label': [],
                'catalog_number': [],
                'combined_artist': '',
                'tracks': [],
                'urls': [],
            }
        })
    elif maptype == 'track':  # only as part of release; recording is different.
        mapping = {'title': [], 'artist': [],
                   'length': [], 'length_formatted': [],
                   'number': [], 'totaltracks': []}
    else:
        raise Exception('unimplemented')
    return mapping

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
        hours = sec // (60 * 60)
        minutes = sec % (60 * 60)
        return '{}:{:02d}:{:02d}'.format(hours, minutes, sec % 60)

def unformat_track_length(length):
    if not length:
        return None
    h_m_s = re.compile(r'^\s*(\d+}):(\d{1,2}):(\d{1,2})\s*$')
    m_s = re.compile(r'^\s*(\d+):(\d{1,2})\s*$')
    ms = re.compile(r'^\s*(\d+)\s*ms\s*$')
    if h_m_s.match(length):
        (h, m, s) = h_m_s.match(length).group(1, 2, 3)
        return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000
    elif m_s.match(length):
        (m, s) = m_s.match(length).group(1, 2)
        return (int(m) * 60 + int(s)) * 1000
    elif ms.match(length):
        return int(ms.match(length).group(1))
    else:
        return None

class MappingBase():
    def code_url_pattern(self):
        return ("https://github.com/metabrainz/geordi/blob/" +
                "master/geordi/geordi/mappings/{0}.py")
