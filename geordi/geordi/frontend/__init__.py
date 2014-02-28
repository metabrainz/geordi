from flask import Blueprint, current_app, render_template, request, abort, redirect, url_for, g, flash
from flask.ext.login import current_user, login_required, login_user, logout_user
from ..db import get_db
import geordi.data as data
from geordi.user import User

import json

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
    ip = get_ip()
    rand = base64.urlsafe_b64encode(os.urandom(30))
    with get_db() as conn, conn.cursor() as curs:
        curs.execute("DELETE FROM csrf WHERE ip = %s AND timestamp < NOW() - interval '1 hour'", (ip,))
        curs.execute('INSERT INTO csrf (ip, csrf, timestamp) VALUES (%s, %s, now())', (ip, rand))
    return rand

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
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('UPDATE csrf SET opts = %s WHERE csrf = %s', (json.dumps(opts), request.args['csrf']))
    return redirect(redirect_uri, code=307)

@frontend.route('/oauth/callback')
def oauth_callback():
    error = request.args.get('error')
    url = url_for('.hello')
    if not error:
        with get_db() as conn:
            csrf = request.args.get('state')
            code = request.args.get('code')
            # look up CSRF token for remember value, returnto URI, and to confirm validity
            with conn.cursor() as curs:
                curs.execute('SELECT opts FROM csrf WHERE csrf = %s AND ip = %s', (csrf,get_ip()))
                if curs.rowcount == 0:
                    flash("CSRF token mismatch. Please try again.")
                    return redirect(url, code=307)
                (opts,) = curs.fetchone()
                curs.execute('DELETE FROM csrf WHERE csrf = %s', (csrf,))
            opts = json.loads(opts)
            remember = opts.get('remember', False)
            url = opts.get('returnto', url)
            # hit oauth2/token for an authorization code, then hit oauth2/userinfo to get a name/tz
            user_data = check_mb_account(code)
            if user_data:
                (username, tz) = user_data
                # add name to DB if needed, update tz
                with conn.cursor() as curs:
                    curs.execute('SELECT tz from editor where name = %s', (username,))
                    if curs.rowcount == 0:
                        curs.execute('INSERT INTO editor (name, tz) VALUES (%s, %s)', (username, tz))
                    elif curs.fetchone()[0] != tz:
                        curs.execute('UPDATE editor SET tz = %s WHERE name = %s', (tz, username))
                login_user(User(username, tz), remember=remember)
                flash("Logged in successfully!")
            else:
                flash('We couldn\'t log you in D:')
                url = url_for('.hello')
    else:
        flash('There was an error: %s' % error)
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
    return redirect(url_for(".hello"))

@frontend.route('/')
def hello():
    return render_template('hello.html')

@frontend.route('/item/<item_id>')
def item(item_id):
    item = data.get_renderable(item_id)
    if item is None:
        abort(404)
    return render_template('item.html', item=item)

#@frontend.route('/data/<index>')
#def list_index(index):
#    pass
#
#@frontend.route('/data/<index>/<item_type>')
#def list_items(index, item_type):
#    pass

@frontend.route('/data/<index>/<item_type>/<data_id>')
def data_item(index, item_type, data_id):
    item_id = data.data_to_item('/'.join([index, item_type, data_id]))
    if item_id is None:
        abort(404)
    else:
        return redirect(url_for('.item', item_id=item_id), code=307)
