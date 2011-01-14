import unittest

from pyramid import testing
from pyramid.config import Configurator

class TestCase(unittest.TestCase):

    def setUp(self):

        self.config = Configurator(autocommit=True)
        self.config.begin()

        #

    def tearDown(self):
        self.config.end()


class TestForm(unittest.TestCase):
    
    def test_is_error(self):
        assert False, "not implemented"

    def test_errors_for(self):
        assert False, "not implemented"

    def test_validate_with_validators(self):
        assert False, "not implemented"

    def test_is_validated_on_post(self):
        assert False, "not implemented"

    def test_validate_good_input(self):
        assert False, "not implemented"

    def test_validate_bad_input(self):
        assert False, "not implemented"
    
    def test_bind(self):
        assert False, "not implemented"

    def test_bind_not_validated_yet(self):
        assert False, "not implemented"

    def test_bind_with_errors(self):
        assert False, "not implemented"

    def test_initialize_with_obj(self):
        assert False, "not implemented"

    def test_variable_decode(self):
        assert False, "not implemented"
    
    def test_validate_from_GET(self):
        assert False, "not implemented"

    def test_validate_csrf(self):
        assert False, "not implemented"


class TestFormRenderer(unittest.TestCase):
    
    def test_render_form(self):
        assert False, "not implemented"

    def test_csrf(self):
        assert False, "not implemented"

    def test_text(self):
        assert False, "not implemented"

    def test_hidden(self):
        assert False, "not implemented"

    def test_select(self):
        assert False, "not implemented"

    def test_file(self):
        assert False, "not implemented"

    def test_radio(self):
        assert False, "not implemented"

    def test_submit(self):
        assert False, "not implemented"

    def test_checkbox(self):
        assert False, "not implemented"
