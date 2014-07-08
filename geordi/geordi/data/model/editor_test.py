from geordi.test_case import GeordiTestCase
from geordi.data.model.editor import Editor
from . import db


class EditorTestCase(GeordiTestCase):

    def test_get(self):
        name = 'Tester'
        editor = Editor(name=name)
        db.session.add(editor)
        db.session.flush()

        same_editor = Editor.get(name)
        assert editor == same_editor

        missing_editor = Editor.get('Unknown')
        assert missing_editor is None

    def test_add_or_update(self):
        editors = Editor.query.all()
        assert len(editors) == 0

        editor_1 = Editor.add_or_update('Tester 1')

        editors = Editor.query.all()
        assert len(editors) == 1
        assert editors[0] == editor_1

        editor_2 = Editor.add_or_update('Tester 1', 'UTC')

        editors = Editor.query.all()
        assert len(editors) == 1
        assert editors[0] == editor_2
        assert editor_1 == editor_2

        editor_3 = Editor.add_or_update('Tester 2')

        editors = Editor.query.all()
        assert len(editors) == 2
        assert editor_3 in editors
        assert editor_2 != editor_3

    def test_delete(self):
        editors = Editor.query.all()
        assert len(editors) == 0

        editor = Editor(name='Tester')
        db.session.add(editor)
        db.session.flush()

        editors = Editor.query.all()
        assert len(editors) == 1

        editor.delete()

        editors = Editor.query.all()
        assert len(editors) == 0
