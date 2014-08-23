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
        self.assertEqual(editor, same_editor)

        missing_editor = Editor.get('Unknown')
        self.assertIsNone(missing_editor)

    def test_add_or_update(self):
        self.assertEqual(Editor.query.count(), 0)

        editor_1 = Editor.add_or_update('Tester 1')

        editors = Editor.query.all()
        self.assertEqual(len(editors), 1)
        self.assertEqual(editors[0], editor_1)

        editor_2 = Editor.add_or_update('Tester 1', 'UTC')

        editors = Editor.query.all()
        self.assertEqual(len(editors), 1)
        self.assertEqual(editors[0], editor_2)
        self.assertEqual(editor_1, editor_2)

        editor_3 = Editor.add_or_update('Tester 2')

        editors = Editor.query.all()
        self.assertEqual(len(editors), 2)
        self.assertIn(editor_3, editors)
        self.assertNotEqual(editor_2, editor_3)

    def test_delete(self):
        self.assertEqual(Editor.query.count(), 0)

        editor = Editor(name='Tester')
        db.session.add(editor)
        db.session.flush()
        self.assertEqual(Editor.query.count(), 1)

        editor.delete()
        self.assertEqual(Editor.query.count(), 0)
