"""
geordi.data.model.entity
------------------------
"""
from . import db
from .mixins import DeleteMixin
from sqlalchemy.dialects.postgresql import UUID

from urllib import urlencode
import urllib2
import json

import logging

logger = logging.getLogger('geordi.data.model.entity')

class Entity(db.Model, DeleteMixin):
    """Model for the 'entity' table, storing materialized information about entities in MusicBrainz."""
    __tablename__ = 'entity'
    __table_args__ = {'schema': 'geordi'}

    #: The entity's MBID.
    mbid = db.Column(UUID, primary_key=True)
    #: The type of entity (e.g. 'release', 'release_group', 'artist', etc.
    type = db.Column(db.Unicode, nullable=False)
    #: Materialized JSON data used to display a link (e.g. the name or title).
    data = db.Column(db.UnicodeText)

    #: Property for matches using this entity.
    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref='entity')

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
            entity = cls(mbid=json_data['mbid'], type=json_data['entityType'], data=json.dumps({'name': json_data['name']}))
            db.session.add(entity)
            #if mbid != json_data['mbid']: handle redirected gids
            db.session.flush()
            return entity
        except urllib2.HTTPError as e:
            logger.debug('Got error %s on opening url %s', e, url)
            return None

    def to_dict(self):
        return {'mbid': self.mbid, 'type': self.type, 'data': json.loads(self.data)}
