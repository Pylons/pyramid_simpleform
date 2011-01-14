import unittest

from formencode import Schema
from formencode import validators

from pyramid import testing
from pyramid.config import Configurator


class SimpleSchema(Schema):

    name = validators.NotEmpty()


class SimpleObj(object):

    def __init__(self, name=None):
        self.name = name


class TestForm(unittest.TestCase):
    
    def test_is_error(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema, validate_csrf=False)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
        self.assert_('name' in form.errors)

    def test_errors_for(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema, validate_csrf=False)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
        self.assert_('name' in form.errors)

        self.assert_(form.errors_for('name') == ['Missing value'])


    def test_validate_good_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()), 
                    validate_csrf=False)

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

    def test_validate_bad_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()), 
                    validate_csrf=False)

        self.assert_(not form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.is_error('name'))

        self.assert_(form.errors_for('name') == ['Missing value'])

    def test_is_validated_on_post(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema, validate_csrf=False)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
 
    def test_validate_good_input(self):
        assert False, "not implemented"

    def test_validate_bad_input(self):
        assert False, "not implemented"
    
    def test_bind(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema, validate_csrf=False)
        form.validate()
        obj = form.bind(SimpleObj())
        self.assert_(obj.name == 'test')
        
    def test_bind_not_validated_yet(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema, validate_csrf=False)
        self.assertRaises(RuntimeError, form.bind, SimpleObj())
 
    def test_bind_with_errors(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = ''

        form = Form(request, SimpleSchema, validate_csrf=False)
        self.assert_(not form.validate())
        self.assertRaises(RuntimeError, form.bind, SimpleObj())
 
    def test_initialize_with_obj(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, obj=SimpleObj(name='test'))

        self.assert_(form.data['name'] == 'test')

    def test_initialize_with_defaults(self):
        assert False, "not implemented"

    def test_initialize_with_obj_and_defaults(self):
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

    def test_label(self):
        assert False, "not implemented"

    def test_label_using_field_name(self):
        assert False, "not implemented"

