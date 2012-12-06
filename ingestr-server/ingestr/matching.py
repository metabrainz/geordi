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
from flask import Response
from flask.ext.login import current_user
from ingestr import app

import json
import uuid
from datetime import datetime

from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])

def make_match_definition(user, matchtype, mbid):
    return {'user': user,
         'timestamp': datetime.utcnow(),
         'type': matchtype,
         'mbid': mbid}

def register_match(index, item, itemtype, matchtype, mbid):
    if not mbid:
        return Response(json.dumps({'code': 400, 'error': 'You must provide an MBID for a match.'}), 400)
    # Check MBID formatting
    try:
        uuid.UUID('{{{uuid}}}'.format(uuid=mbid))
    except ValueError:
        return Response(json.dumps({'code': 400, 'error': 'The provided MBID is ill-formed'}), 400)
    # Retrieve document (or blank empty document for subitems)
    try:
        document = es.get(index, itemtype, item)
        data = document['_source']
        version = document['_version']
    except ElasticHttpNotFoundError:
        if itemtype == 'item':
            return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404)
        else:
            data = {}
            version = None

    if '_ingestr' not in data:
        data['_ingestr'] = {}
    if 'matchings' not in data['_ingestr']:
        data['_ingestr']['matchings'] = []

    data['_ingestr']['matchings'].append(make_match_definition(current_user.id, matchtype, mbid))

    try:
        if version:
            es.index(index, itemtype, data, id=item, es_version=version)
        else:
            es.index(index, itemtype, data, id=item)
        return Response(json.dumps({'code': 200}), 200)
    except:
        return Response(json.dumps({'code': 500, 'error': 'An unknown error happened while pushing to elasticsearch.'}), 500)
