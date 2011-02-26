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

class TestState(unittest.TestCase):

    def test_state(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assert_(obj.foo=="bar")

    def test_state_contains(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assert_("foo" in obj)

    def test_state_not_contains(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assert_("bar" not in obj)

    def test_getitem(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assert_(obj['foo'] == 'bar')

    def test_setitem(self):

        from pyramid_simpleform import State
        obj = State()
        obj['foo'] = "bar"
        self.assert_(obj['foo'] == 'bar')
        self.assert_(obj.foo == 'bar')

    def test_get(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assert_(obj.get('foo') == 'bar')
        self.assert_(obj.get('bar', 'foo') == 'foo')


class TestForm(unittest.TestCase):
    

    def test_is_error(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
        self.assert_('name' in form.errors)

    def test_all_errors_with_single_string(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.errors = u"Name is missing"
        self.assert_(form.all_errors() == [u"Name is missing"])

    def test_all_errors_with_list(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.errors = [u"Name is missing"]
        self.assert_(form.all_errors() == [u"Name is missing"])

    def test_all_errors_with_dict(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.errors = {"name" : [u"Name is missing"],
                       "value" : u"Value is missing"}
        self.assert_(form.all_errors() == [
            u"Name is missing", 
            u"Value is missing"])

    def test_errors_for(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
        self.assert_('name' in form.errors)

        self.assert_(form.errors_for('name') == ['Missing value'])

    def test_validate_twice(self):
        
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

        request.POST = {'name' : 'ok again'}

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

    def test_validate_good_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

    def test_validate_bad_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assert_(not form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.is_error('name'))

        self.assert_(form.errors_for('name') == ['Please enter a value'])

    def test_is_validated_on_post(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
 
    def test_bind(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()
        obj = form.bind(SimpleObj())
        self.assert_(obj.name == 'test')

    def test_bind_ignore_underscores(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'
        request.POST['_ignoreme'] = 'test'

        class SimpleObjWithPrivate(SimpleObj):
            _ignoreme = None

        class SimpleSchemaWithPrivate(SimpleSchema):
            _ignoreme = validators.String()

        form = Form(request, SimpleSchemaWithPrivate)
        form.validate()
        obj = form.bind(SimpleObjWithPrivate())
        self.assert_(obj.name == 'test')
        self.assert_(obj._ignoreme is None)
        
    def test_bind_not_validated_yet(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        self.assertRaises(RuntimeError, form.bind, SimpleObj())
 
    def test_bind_with_errors(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = ''

        form = Form(request, SimpleSchema)
        self.assert_(not form.validate())
        self.assertRaises(RuntimeError, form.bind, SimpleObj())

    def test_bind_with_exclude(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()
        obj = form.bind(SimpleObj(), exclude=["name"])
        self.assert_(obj.name == None)
 
    def test_bind_with_include(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()
        obj = form.bind(SimpleObj(), include=['foo'])
        self.assert_(obj.name == None)
 
    def test_initialize_with_obj(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, obj=SimpleObj(name='test'))

        self.assert_(form.data['name'] == 'test')

    def test_initialize_with_defaults(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={'name' : 'test'})

        self.assert_(form.data['name'] == 'test')

    def test_initialize_with_obj_and_defaults(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, 
                    obj=SimpleObj(name='test1'),
                    defaults={'name' : 'test2'})

        self.assert_(form.data['name'] == 'test1')

    def test_variable_decode(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.method = "POST"
        
        form = Form(request, SimpleSchema,
                    variable_decode=True)

        self.assert_(form.validate())
        self.assert_(form.data['name'] == 'test')

    def test_validate_from_GET(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "GET"
        request.GET['name'] = 'test'

        form = Form(request, SimpleSchema, method="GET")

        self.assert_(form.validate())
        self.assert_(form.is_validated)
 
    def test_render_without_htmlfill(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.method = "POST"
        
        settings = {}

        settings['mako.directories'] = 'pyramid_simpleform:templates'
        config = Configurator(settings=settings)


        config.add_renderer('.html', 
                            'pyramid.mako_templating.renderer_factory')

        request.registry = config.registry

        form = Form(request, SimpleSchema)

        result = form.render("test_form.html", htmlfill=False)
        self.assert_('<input type="text" name="name" size="20">' 
                     in result)


    def test_render_with_htmlfill(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.method = "POST"
        
        settings = {}

        settings['mako.directories'] = 'pyramid_simpleform:templates'
        config = Configurator(settings=settings)


        config.add_renderer('.html', 
                            'pyramid.mako_templating.renderer_factory')

        request.registry = config.registry

        form = Form(request, SimpleSchema, defaults={'name' : 'foo'})

        result = form.render("test_form.html", htmlfill=True)
        self.assert_('<input type="text" name="name" size="20" value="foo">' 
                     in result)


    def test_htmlfill(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, 
                    defaults={"name" : "testing"})

        html = """
        <form method="POST" action=".">
            <input type="text" name="name">
        </form>
        """

        html = form.htmlfill(html)
        self.assert_('value="testing"' in html)


class TestFormRenderer(unittest.TestCase):
    
    def test_begin_form(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.begin(url="/"),
                     '<form action="/" method="post">')

    def test_end_form(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.end() == "</form>")

    def test_csrf(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.csrf() == \
            '<input id="_csrf" name="_csrf" type="hidden" value="csrft" />')
 
    def test_csrf_token(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.csrf_token() == \
                '<div style="display:none;"><input id="_csrf" name="_csrf" '
                'type="hidden" value="csrft" /></div>')

    def test_hidden_tag_with_csrf_and_other_names(self):
        
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={'name':'foo'})
        renderer = FormRenderer(form)

        self.assert_(renderer.hidden_tag('name') == \
            '<div style="display:none;"><input id="name" name="name" '
            'type="hidden" value="foo" /><input id="_csrf" name="_csrf" '
            'type="hidden" value="csrft" /></div>')

    def test_hidden_tag_with_just_csrf(self):
        
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.hidden_tag() == \
                '<div style="display:none;"><input id="_csrf" name="_csrf" '
                'type="hidden" value="csrft" /></div>')


 
 
 
    def test_text(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assert_(renderer.text("name") == \
                '<input id="name" name="name" type="text" value="Fred" />')

    def test_textarea(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assert_(renderer.textarea("name") == \
                '<textarea id="name" name="name">Fred</textarea>')
 
    def test_hidden(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assert_(renderer.hidden("name") == \
                '<input id="name" name="name" type="hidden" value="Fred" />')
        
    def test_select(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)
        
        options = [
            ("Fred", "Fred"),
            ("Barney", "Barney"),
            ("Wilma", "Wilma"),
            ("Betty", "Betty"),
        ]   

        self.assert_(renderer.select("name", options) == \
            """<select id="name" name="name">
<option selected="selected" value="Fred">Fred</option>
<option value="Barney">Barney</option>
<option value="Wilma">Wilma</option>
<option value="Betty">Betty</option>
</select>""")
 
    def test_file(self):
  
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.file('file') == \
                   '<input id="file" name="file" type="file" />')

    def test_password(self):
  
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.password('password') == \
                   '<input id="password" name="password" type="password" />')


    def test_radio(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : 'Fred'})
        renderer = FormRenderer(form)
        
        self.assert_(renderer.radio("name", value="Fred") == \
                     '<input checked="checked" id="name_fred" name="name" '
                     'type="radio" value="Fred" />')
        
        self.assert_(renderer.radio("name", value="Barney") == \
                     '<input id="name_barney" name="name" '
                     'type="radio" value="Barney" />')

    def test_submit(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.submit("submit", "Submit") == \
            '<input id="submit" name="submit" type="submit" value="Submit" />')

    def test_checkbox(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : True})
        renderer = FormRenderer(form)
        
        self.assert_(renderer.checkbox("name") == \
            '<input checked="checked" id="name" name="name" type="checkbox" '
            'value="1" />')

    def test_is_error(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))

        renderer = FormRenderer(form)
        self.assert_(renderer.is_error('name'))

    def test_errors_for(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        renderer = FormRenderer(form)

        self.assert_(renderer.errors_for('name') == ['Missing value'])

    def test_errorlist(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist() == \
                     '<ul class="error"><li>Missing value</li></ul>')
     

    def test_errorlist_with_no_errors(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist() == '')

    def test_errorlist_with_custom_localizer(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform import State
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        state = State(_=lambda s:s.upper())

        form = Form(request, SimpleSchema, state=state)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist('name') == \
                     '<ul class="error"><li>MISSING VALUE</li></ul>')
 
 
    def test_errorlist_with_field(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist('name') == \
                     '<ul class="error"><li>Missing value</li></ul>')
 
    def test_label(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.label("name") == \
                   '<label for="name">Name</label>') 

    def test_label_using_field_name(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.label("name", "Your name") == \
                   '<label for="name">Your name</label>') 

