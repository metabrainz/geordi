from flask import Blueprint, current_app, render_template, request, abort, redirect, url_for, g, flash, jsonify
from flask.ext.login import current_user, login_required, login_user, logout_user
import geordi.data as data
from geordi.data.mapping.extract import extract_value
from geordi.data.model import db
from geordi.data.model.csrf import CSRF
from geordi.data.model.editor import Editor
from geordi.data.model.item import Item
from geordi.data.model.item_data import ItemData
from geordi.user import User

import json
import re

from urllib import urlencode
import base64
import os
import urllib2

frontend = Blueprint('frontend', __name__)

@frontend.before_request
def before_request():
    if current_user.get_id():
        pass
    elif request.endpoint.split('.')[1] not in ['login_redirect', 'oauth_callback']:
        g.login_parameters = {
            "csrf": get_csrf(),
            "returnto": request.url
        }

def get_ip():
    try:
        proxies = request.environ['HTTP_X_FORWARDED_FOR'].split(',')
        return [x for x in proxies if x not in current_app.config['TRUSTED_PROXIES']][-1]
    except KeyError:
        try:
            return request.environ['HTTP_X_MB_REMOTE_ADDR']
        except KeyError:
            return request.environ['REMOTE_ADDR']

def get_csrf():
    if not current_app.config['TESTING']:
        rand = base64.urlsafe_b64encode(os.urandom(30))
        ip = get_ip()
        CSRF.update_csrf(ip, rand)
        db.session.commit()
        return rand
    else:
        return 'test'

@frontend.route('/oauth/login_redirect')
def login_redirect():
    args = urlencode({
        'client_id': current_app.config['OAUTH_CLIENT_ID'],
        'redirect_uri': current_app.config['OAUTH_REDIRECT_URI'],
        'state': request.args['csrf'],
        'response_type': 'code',
        'scope': 'profile'
    })
    redirect_uri = 'https://musicbrainz.org/oauth2/authorize?%s' % args
    # Update csrf row with the remember me option and returnto URI
    opts = {}
    if request.args.get('remember'):
        opts['remember'] = True
    if request.args.get('returnto'):
        opts['returnto'] = request.args.get('returnto')
    CSRF.get(request.args['csrf']).opts = json.dumps(opts)
    db.session.commit()
    return redirect(redirect_uri, code=307)

@frontend.route('/oauth/callback')
def oauth_callback():
    error = request.args.get('error')
    url = url_for('.homepage')
    if not error:
        csrf = request.args.get('state')
        code = request.args.get('code')
        # look up CSRF token for remember value, returnto URI, and to confirm validity
        stored_csrf = CSRF.get(csrf=csrf, ip=get_ip())
        if stored_csrf is None:
            flash("CSRF token mismatch. Please try again.")
            return redirect(url, code=307)
        opts = json.loads(stored_csrf.opts)
        stored_csrf.delete()
        remember = opts.get('remember', False)
        url = opts.get('returnto', url)
        # hit oauth2/token for an authorization code, then hit oauth2/userinfo to get a name/tz
        user_data = check_mb_account(code)
        if user_data:
            (username, tz) = user_data
            Editor.add_or_update(username, tz)
            login_user(User(username, tz), remember=remember)
            flash("Logged in successfully!")
        else:
            flash("We couldn't log you in D:")
            url = url_for('.homepage')
    else:
        flash('There was an error: %s' % error)
    db.session.commit()
    return redirect(url, code=307)

def check_mb_account(auth_code):
    url = 'https://musicbrainz.org/oauth2/token'
    data = urlencode({'grant_type': 'authorization_code',
                      'code': auth_code,
                      'client_id': current_app.config['OAUTH_CLIENT_ID'],
                      'client_secret': current_app.config['OAUTH_CLIENT_SECRET'],
                      'redirect_uri': current_app.config['OAUTH_REDIRECT_URI']})
    json_data = json.load(urllib2.urlopen(url, data))

    url = 'https://beta.musicbrainz.org/oauth2/userinfo'
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'Bearer ' + json_data['access_token'])]
    try:
        userdata = json.load(opener.open(url, timeout=5))
        return (userdata['sub'], userdata.get('zoneinfo'))
    except StandardError:
        return None

@frontend.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for(".homepage"))

@frontend.route('/')
def homepage():
    return render_template('homepage.html')

@frontend.route('/item/<int:item_id>')
def item(item_id):
    item = data.get_renderable(item_id)
    if item is None:
        abort(404)
    return render_template('item.html', item=item)

@frontend.route('/item/<int:item_id>/links')
def item_links(item_id):
    item = Item.get(item_id)
    if item is None:
        abort(404)

    linked_items = {}
    for item_link in set(item.items_linked):
        linked_items[item_link.item_id] = Item.get(item_link.item_id)

    def to_int_conditionally(val):
        return int(val) if re.match('^\d+$', val) else val

    links = []
    for item_link in item.items_linked:
        path = [to_int_conditionally(x) for x in item_link.type.split('%')]
        links.append(dict(
            item_id=item_link.item_id,
            path=item_link.type,
            value=extract_value(linked_items[item_link.item_id].map_dict, path)[0][1],
        ))

    return render_template('item_links.html', item=item, links=links, linked_items=linked_items)

#@frontend.route('/entity/<mbid>')
#@login_required
#def entity_data(mbid):
#    with get_db() as conn:
#        use_cache = not request.args.get('no_cache', False)
#        type_hint = request.args.get('type_hint', None)
#        if use_cache:
#            # entity = data.get_entities(mbid, conn=conn, cached=True, type_hint=type_hint)
#            # check DB for this MBID, return if present
#            pass
#        if not entity:
#            # entity = data.get_entities(mbid, conn=conn, cached=False, type_hint=type_hint)
#            # fetch remotely and put in DB.
#            pass
#        return jsonify({})
#
#@frontend.route('/item/<item_id>/match', methods=['POST'])
#@login_required
#def match_item(item_id):
#    '''This endpoint is passed a set of mbids, and an item.
#    It then checks if the set matches the current match for the item;
#    if so, it does nothing. If not, the submitted match becomes the
#    new match, superseding the former match. As a precaution, empty
#    sets will be ignored unless a special extra parameter is set.
#    '''
#    is_mbid = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
#    empty = request.form.get('empty', False)
#    mbids = [mbid.lower() for mbid in request.form.getlist('matches')]
#    if len(mbids) == 0 and not empty:
#        return jsonify({'error': 'No matches provided.'})
#    if len([True for mbid in mbids if (is_mbid.match(mbid) is None)]) > 0:
#        return jsonify({'error': 'MBIDs improperly formatted.'})
#    with get_db() as conn:
#        ## fetch existing matches from the DB
#        #existing = data.get_matches(item_id, conn=conn)
#        #if set(mbids) == set(existing):
#        #    return jsonify({'error': 'Matches not changed'})
#        ## add new matches if applicable
#        #entities = data.get_entities(mbids, conn=conn, cached=False) # check error condition?
#        #success = data.add_matches(item_id, mbids, conn=conn)
#        ## return JSON success value and matches preserved/added/superseded
#        pass
#    return jsonify({})

@frontend.route('/data')
def list_indexes():
    indexes = ItemData.get_indexes()
    return render_template('indexes.html', indexes=indexes)

@frontend.route('/data/<index>')
def list_index(index):
    item_types = ItemData.get_item_types_by_index(index)
    if not item_types:
        abort(404)
    return render_template('index.html', item_types=item_types, index=index)

@frontend.route('/data/<index>/<item_type>')
def list_items(index, item_type):
    item_ids = ItemData.get_item_ids(index, item_type)
    if not item_ids:
        abort(404)
    return render_template('itemtype.html', items=item_ids, item_type=item_type, index=index)

@frontend.route('/data/<index>/<item_type>/<path:data_id>')
def data_item(index, item_type, data_id):
    item_id = ItemData.data_to_item('/'.join([index, item_type, data_id]))
    if not item_id:
        abort(404)
    return redirect(url_for('.item', item_id=item_id), code=307)
