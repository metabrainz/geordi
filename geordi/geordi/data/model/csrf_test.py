from geordi.test_case import GeordiTestCase
from geordi.data.model.csrf import CSRF
from datetime import datetime, timedelta
from . import db


class CSRFTestCase(GeordiTestCase):

    def test_get(self):
        csrf = CSRF(ip='127.0.0.1', csrf='some_random_string')
        db.session.add(csrf)
        db.session.flush()

        same_csrf = CSRF.get('some_random_string')
        self.assertEqual(csrf, same_csrf)

        missing_csrf = CSRF.get('another_random_string')
        self.assertIsNone(missing_csrf)

    def test_update(self):
        self.assertEqual(CSRF.query.count(), 0)

        ip = '127.0.0.1'

        # Adding first row that will be removed later
        csrf_1 = CSRF(ip=ip, csrf='random', timestamp=datetime.today() - timedelta(hours=2))
        db.session.add(csrf_1)
        db.session.flush()
        self.assertEqual(CSRF.query.count(), 1)

        CSRF.update_csrf(ip, 'another_random')

        # csrf_1 should be replaced with the new row.
        rows = CSRF.query.all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].ip, ip)
        self.assertEqual(rows[0].csrf, 'another_random')

        # If we update one more time within 1 hour, both rows should be present.
        CSRF.update_csrf(ip, 'one_more_random')
        self.assertEqual(CSRF.query.count(), 2)
