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

from __future__ import division, absolute_import
def check_data_format(data):
    "Initialize or correct the special _geordi key in the document"
    data.setdefault('_geordi', {
            'mapping': {'version': 0},
            'links': {'links': [], 'version': 1},
            'matchings': {'matchings': [], 'auto_matchings': [], 'current_matching': {}, 'version': 3}
    })

    data['_geordi'].setdefault('mapping', {'version': 0})
    data['_geordi'].setdefault('links', {'links': [], 'version': 1})
    data['_geordi'].setdefault('matchings', {'matchings': [], 'auto_matchings': [], 'current_matching': {}, 'version': 2})

    if 'auto_matchings' not in data['_geordi']['matchings']:
        data['_geordi']['matchings']['auto_matchings'] = []
        data['_geordi']['matchings']['version'] = 2

    return data

def uniq(list):
    seen = []
    return [c for c in list if not (c in seen or seen.append(c))]
