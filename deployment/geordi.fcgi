#!/var/www/geordi/env/bin/python2
# ^ change to relevant virtualenv
import sys
sys.path.insert(0, '/var/www/geordi/geordi/geordi')
# ^ change to relevant path to geordi root

from flup.server.fcgi import WSGIServer
from geordi import app

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/tmp/geordi-fcgi.sock').run()
    # ^ change to relevant unix socket
