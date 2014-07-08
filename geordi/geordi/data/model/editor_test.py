from geordi.test_case import GeordiTestCase
from geordi.data.model.editor import Editor


class EditorTestCase(GeordiTestCase):

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
