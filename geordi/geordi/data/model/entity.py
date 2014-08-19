"""
geordi.data.model.entity
------------------------
"""
from . import db
from .mixins import DeleteMixin
from geordi.data.model.raw_match_entity import RawMatchEntity
from sqlalchemy.dialects.postgresql import UUID

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
    raw_match_entities = db.relationship('RawMatchEntity', passive_deletes='all', backref=db.backref('entity', lazy='joined'))

    @classmethod
    def get(cls, mbid, **kwargs):
        return cls.query.filter_by(mbid=mbid, **kwargs).first()

    @classmethod
    def get_remote(cls, mbid, **kwargs):
        url = 'https://musicbrainz.org/ws/js/entity/%s' % mbid
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept', 'application/json')]
        existing = cls.get(mbid)
        try:
            json_data = json.load(opener.open(url, timeout=5))
            if mbid != json_data['gid']:
                existing_target = cls.get(json_data['gid'])
                if existing and existing_target:
                    existing = existing.merge_into(existing_target)
                elif not existing:
                    existing = existing_target

            if existing:
                existing.mbid = json_data['gid']
                existing.type = json_data['entityType']
                existing.data = json.dumps({'name': json_data['name']})
                entity = existing
            else:
                entity = cls(mbid=json_data['gid'], type=json_data['entityType'], data=json.dumps({'name': json_data['name']}))
                db.session.add(entity)
            db.session.flush()
            return entity
        except urllib2.HTTPError as e:
            logger.debug('Got error %s on opening url %s', e, url)
            return None

    def merge_into(self, target):
        RawMatchEntity.query.filter_by(entity_mbid=self.mbid).update({'entity_mbid': target.mbid})
        self.delete()
        return target

    def to_dict(self):
        if self.data is None:
            self.data = '{}'
        return {'mbid': self.mbid, 'type': self.type, 'data': json.loads(self.data)}
