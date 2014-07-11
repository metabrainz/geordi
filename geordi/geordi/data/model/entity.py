from . import db
from sqlalchemy.dialects.postgresql import UUID

from urllib import urlencode
import urllib2
import json

import logging

logger = logging.getLogger('geordi.data.model.entity')

class Entity(db.Model):
    __tablename__ = 'entity'
    __table_args__ = {'schema': 'geordi'}

    mbid = db.Column(UUID, primary_key=True)
    type = db.Column(db.Unicode, nullable=False)
    data = db.Column(db.UnicodeText)

    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref=db.backref('entity', lazy='joined'))

    @classmethod
    def get(cls, mbid, **kwargs):
        return cls.query.filter_by(mbid=mbid, **kwargs).first()

    @classmethod
    def get_remote(cls, mbid, **kwargs):
        url = 'https://musicbrainz.org/ws/js/entity/%s' % mbid
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept', 'application/json')]
        try:
            json_data = json.load(opener.open(url, timeout=5))
            entity = cls(mbid=json_data['gid'], type=json_data['entityType'], data=json.dumps({'name': json_data['name']}))
            db.session.add(entity)
            #if mbid != json_data['mbid']: handle redirected gids
            db.session.flush()
            return entity
        except urllib2.HTTPError as e:
            logger.debug('Got error %s on opening url %s', e, url)
            return None

    def delete(self):
        db.session.delete(self)
        db.session.flush()
        return self

    def to_dict(self):
        return {'mbid': self.mbid, 'type': self.type, 'data': json.loads(self.data)}
