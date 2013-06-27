# geordi
# Copyright (C) 2013 Ian McEwen, MetaBrainz Foundation
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

from flask import Blueprint, request, Response, json
from flask.ext.login import current_user

from geordi.data import resolve_data, get_search_params, get_subitem
from geordi.mappings import get_link_types_by_index, get_matching_enabled_by_index
from geordi.matching import register_match

from pyelasticsearch import ElasticHttpNotFoundError

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/search')
def apisearch():
    "Perform a search, returning JSON"
    params = get_search_params()
    if 'error' in params:
        response = Response(json.dumps({'code': 400, 'error': params['error']}), 400, mimetype="application/json")
    else:
        response = Response(json.dumps({'code': 200, 'result': params.get('data'), 'mapping': params.get('mapping')}), 200, mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@bp.route('/item/<index>/<item>')
def item(index, item):
    "Get information for an item"
    try:
        document = resolve_data(index, item)
        if request.args.get('subitems', False):
            link_types = get_link_types_by_index(index)
            for (link_type, links) in document['_source']['_geordi']['links']['links'].iteritems():
                if link_type != 'version':
                    for link in links:
                        subitem = "{}-{}".format(link_type, link[link_types[link_type]['key']])
                        get_subitem(index, subitem, create=True, seed=copy.deepcopy(link))
        response = Response(json.dumps({'code': 200, 'document': document}), 200, mimetype="application/json")
    except ElasticHttpNotFoundError:
        response = Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@bp.route('/matchitem/<index>/<item>')
def matchitem(index, item):
    "Submit a match for this item"
    if get_matching_enabled_by_index(index):
        if current_user.is_authenticated():
            auto = False
            user = None
            if request.args.get('unmatch', False):
                return register_match(index, item, 'item', 'unmatch', [], auto, user)
        else:
            auto = True
            user = request.args.get('user')
            if user in ['matched by index']:
                return Response(json.dumps({'code': 400, 'error': 'The name "{}" is reserved.'.format(user)}), 400, mimetype="application/json")
        matchtype = request.args.get('type', 'release')
        mbids = request.args.getlist('mbid')
        if not mbids:
            mbids = re.split(',\s*', request.args.get('mbids'))
        return register_match(index, item, 'item', matchtype, mbids, auto, user)
    else:
        return Response(json.dumps({'code': 400, 'error': 'Matching is not enabled for this index'}), 400, mimetype="application/json")

@bp.route('/subitem/<index>/<subitem>')
def subitem(index, subitem):
    "Get information for a subitem's matching"
    subitem = get_subitem(index, subitem)
    if subitem:
        response = Response(json.dumps({'code': 200, 'document': subitem}), 200, mimetype="application/json")
    else:
        response = Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@bp.route('/matchsubitem/<index>/<subitem>')
def matchsubitem(index, subitem):
    "Submit a match for this subitem"
    if get_matching_enabled_by_index(index):
        if current_user.is_authenticated():
            auto = False
            user = None
            if request.args.get('unmatch', False):
                return register_match(index, subitem, 'subitem', 'unmatch', [], auto, user)
        else:
            auto = True
            user = request.args.get('user')
        matchtype = request.args.get('type', 'artist')
        mbids = request.args.getlist('mbid')
        if not mbids:
            mbids = re.split(',\s*', request.args.get('mbids'))
        return register_match(index, subitem, 'subitem', matchtype, mbids, auto, user)
    else:
        return Response(json.dumps({'code': 400, 'error': 'Matching is not enabled for this index'}), 400, mimetype="application/json")
