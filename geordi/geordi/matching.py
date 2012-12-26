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
from flask import Response, request
from flask.ext.login import current_user
from geordi import app, es
from geordi.utils import check_data_format

import json
import uuid
import urllib2
from datetime import datetime

from pyelasticsearch import ElasticHttpNotFoundError

def make_match_definition(user, matchtype, mbids, auto=False, ip=False):
    match = {'user': user,
            'timestamp': datetime.utcnow(),
            'type': matchtype,
            'mbid': mbids,
            'auto': True if auto else False,
            'version': 1}
    if ip:
        match['ip'] = ip
    return match

def check_type(mbid):
    req = urllib2.Request('http://musicbrainz.org/ws/js/entity/{mbid}'.format(mbid=mbid))
    req.add_header('User-Agent', 'Geordi +http://geordi.musicbrainz.org/')
    req.add_header('Accept', 'application/json')
    try:
        res = urllib2.urlopen(req)
        j = json.load(res)
        return {"type": j['type']}
    except urllib2.HTTPError, e:
        return {"error": "failed", "code": e}

def register_match(index, item, itemtype, matchtype, mbids, auto=False, user=None, ip=False):
    if matchtype != 'unmatch':
        if len(mbids) < 1:
            response = Response(json.dumps({'code': 400, 'error': 'You must provide at least one MBID for a match.'}), 400, mimetype="application/json")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        # Check MBID formatting
        try:
            [uuid.UUID('{{{uuid}}}'.format(uuid=mbid)) for mbid in mbids]
        except ValueError:
            response = Response(json.dumps({'code': 400, 'error': 'A provided MBID is ill-formed'}), 400, mimetype="application/json")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        for mbid in mbids:
            check = check_type(mbid)
            if 'error' in check:
                response = Response(json.dumps({'code': 400, 'error': 'MBID {} cannot be found in MusicBrainz'.format(mbid)}), 400, mimetype="application/json")
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            elif check['type'] != matchtype:
                response = Response(json.dumps({'code': 400, 'error': 'Provided match type {provided} doesn\'t match type {mbidtype} of {mbid}'.format(provided=matchtype, mbidtype=check['type'], mbid=mbid)}), 400, mimetype="application/json")
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            else: continue

    # Retrieve document (or blank empty document for subitems)
    try:
        document = es.get(index, itemtype, item)
        data = document['_source']
        version = document['_version']
    except ElasticHttpNotFoundError:
        if itemtype == 'item':
            response = Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            data = {}
            version = None

    data = check_data_format(data)

    if auto:
        if not user:
            response = Response(json.dumps({'code': 400, 'error': 'Automatic matches must provide a name.'}), 400, mimetype="application/json")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        if not ip:
            try:
                ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
            except KeyError:
                ip = request.environ['REMOTE_ADDR']
    else:
        user = current_user.id
        ip = False

    match = make_match_definition(user, matchtype, mbids, auto, ip)
    if ((not auto or
        len(data['_geordi']['matchings']['matchings']) == 0 or
        data['_geordi']['matchings']['current_matching']['auto'])
          and matchtype != 'unmatch'):
        data['_geordi']['matchings']['current_matching'] = match
    if not auto:
        data['_geordi']['matchings']['matchings'].append(match)
    else:
        data['_geordi']['matchings']['auto_matchings'].append(match)

    if matchtype == 'unmatch':
        data['_geordi']['matchings']['current_matching'] = {}

    try:
        if version:
            es.index(index, itemtype, data, id=item, es_version=version)
        else:
            es.index(index, itemtype, data, id=item)
        response = Response(json.dumps({'code': 200}), 200, mimetype="application/json")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except:
        response = Response(json.dumps({'code': 500, 'error': 'An unknown error happened while pushing to elasticsearch.'}), 500, mimetype="application/json")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
