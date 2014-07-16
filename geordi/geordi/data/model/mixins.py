"""
geordi.data.model.mixins
------------------------

Helpful mixin classes for commonalities between models.
"""
from . import db


class DeleteMixin(object):
    """Provides a 'delete' method deleting an object from the DB."""
    def delete(self):
        """Delete this object from the DB."""
        db.session.delete(self)
        db.session.flush()
        return self
