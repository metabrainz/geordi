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
from flask import Response
from flask.ext.login import current_user
from geordi import app
from geordi.mappings import check_data_format

import json
import uuid
from datetime import datetime

from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])

def make_match_definition(user, matchtype, mbids, auto=False):
    return {'user': user,
            'timestamp': datetime.utcnow(),
            'type': matchtype,
            'mbid': mbids,
            'auto': True if auto else False,
            'version': 1}

def register_match(index, item, itemtype, matchtype, mbids, auto=False, user=None):
    if len(mbids) < 1:
        return Response(json.dumps({'code': 400, 'error': 'You must provide at least one MBID for a match.'}), 400, mimetype="application/json")
    # Check MBID formatting
    try:
        [uuid.UUID('{{{uuid}}}'.format(uuid=mbid)) for mbid in mbids]
    except ValueError:
        return Response(json.dumps({'code': 400, 'error': 'A provided MBID is ill-formed'}), 400, mimetype="application/json")
    # Retrieve document (or blank empty document for subitems)
    try:
        document = es.get(index, itemtype, item)
        data = document['_source']
        version = document['_version']
    except ElasticHttpNotFoundError:
        if itemtype == 'item':
            return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")
        else:
            data = {}
            version = None

    data = check_data_format(data)

    if auto:
        if not user:
            return Response(json.dumps({'code': 400, 'error': 'Automatic matches must provide a name.'}), 400, mimetype="application/json")
    else:
        user = current_user.id

    match = make_match_definition(user, matchtype, mbids, auto)
    if (not auto or
        len(data['_geordi']['matchings']['matchings']) == 0 or
        data['_geordi']['matchings']['current_matching']['auto']):
        data['_geordi']['matchings']['current_matching'] = match
    if not auto:
        data['_geordi']['matchings']['matchings'].append(match)
    else:
        data['_geordi']['matchings']['auto_matchings'].append(match)

    try:
        if version:
            es.index(index, itemtype, data, id=item, es_version=version)
        else:
            es.index(index, itemtype, data, id=item)
        return Response(json.dumps({'code': 200}), 200, mimetype="application/json")
    except:
        return Response(json.dumps({'code': 500, 'error': 'An unknown error happened while pushing to elasticsearch.'}), 500, mimetype="application/json")
