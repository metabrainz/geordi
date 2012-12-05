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
from ingestr import app

from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

def do_search(query_string, indices, start_from=None):
    es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])
    if indices in [[], ['']]:
        indices = app.config['AVAILABLE_INDICES']
    query = {'query':
              {'bool': {'must': [
                {"query_string": {"query": query_string}}
              ]}}
            }
    if start_from:
        query['from'] = start_from
    return es.search(query, index = indices, doc_type = "item")
