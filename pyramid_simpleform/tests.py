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
    
    def test_is_validated_on_post(self):
        pass


    def test_validate_good_input(self):
        pass


    def test_validate_bad_input(self):
        pass

    
    def test_bind(self):
        pass

    def test_initialize_with_obj(self):
        pass

    def test_variable_decode(self):
        pass
    
    def test_validate_from_GET(self):
        pass

    def test_validate_csrf(self):
        pass


class TestFormRenderer(unittest.TestCase):
    pass
