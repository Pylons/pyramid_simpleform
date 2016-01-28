import unittest

import formencode
from formencode import Schema
from formencode import validators

try:
    from webhelpers2.html.tags import Option, Options, OptGroup
except ImportError:
    from webhelpers.html.tags import Option, Options, OptGroup

from pyramid import testing
from pyramid.config import Configurator


class SimpleFESchema(Schema):

    name = validators.NotEmpty()
    names = formencode.ForEach()


class SimpleObj(object):

    def __init__(self, name=None):
        self.name = name


class TestState(unittest.TestCase):

    def test_state(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assertTrue(obj.foo=="bar")

    def test_state_contains(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assertTrue("foo" in obj)

    def test_state_not_contains(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assertTrue("bar" not in obj)

    def test_getitem(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assertTrue(obj['foo'] == 'bar')

    def test_getitem_notfound(self):

        from pyramid_simpleform import State
        obj = State()
        self.assertRaises(KeyError, obj.__getitem__, 'foo')

    def test_setitem(self):

        from pyramid_simpleform import State
        obj = State()
        obj['foo'] = "bar"
        self.assertTrue(obj['foo'] == 'bar')
        self.assertTrue(obj.foo == 'bar')

    def test_get(self):

        from pyramid_simpleform import State
        obj = State(foo="bar")
        self.assertTrue(obj.get('foo') == 'bar')
        self.assertTrue(obj.get('bar', 'foo') == 'foo')


class TestFormencodeForm(unittest.TestCase):
    
    def test_is_error(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)

        self.assertTrue(not(form.validate()))
        self.assertTrue(form.is_validated)
        self.assertTrue('name' in form.errors)

    def test_all_errors_with_single_string(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)
        form.errors = u"Name is missing"
        self.assertTrue(form.all_errors() == [u"Name is missing"])

    def test_all_errors_with_list(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)
        form.errors = [u"Name is missing"]
        self.assertTrue(form.all_errors() == [u"Name is missing"])

    def test_ok_with_jsonbody(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        
        import json
        request.json_body = json.loads('{"name" : "ok"}')
        
        form = Form(request, SimpleFESchema)
        self.assertTrue(form.validate())

    def test_error_with_jsonbody(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        
        import json
        request.json_body = json.loads('{}')
        
        form = Form(request, SimpleFESchema)
        form.errors = {"name" : [u"Name is missing"],
                       "value" : u"Value is missing"}
        self.assertTrue(sorted(form.all_errors()) == sorted([
            u"Name is missing", 
            u"Value is missing"]))

        
    def test_all_errors_with_dict(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)
        form.errors = {"name" : [u"Name is missing"],
                       "value" : u"Value is missing"}
        self.assertTrue(sorted(form.all_errors()) == sorted([
            u"Name is missing", 
            u"Value is missing"]))

    def test_errors_for(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)

        self.assertTrue(not(form.validate()))
        self.assertTrue(form.is_validated)
        self.assertTrue('name' in form.errors)

        self.assertTrue(form.errors_for('name') == ['Missing value'])

    def test_validate_twice(self):
        
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assertTrue(form.validate())
        self.assertTrue(form.is_validated)
        self.assertTrue(form.data['name'] == 'ok')

        request.POST = {'name' : 'ok again'}

        self.assertTrue(form.validate())
        self.assertTrue(form.is_validated)
        self.assertTrue(form.data['name'] == 'ok')

    def test_validate_good_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assertTrue(form.validate())
        self.assertTrue(form.is_validated)
        self.assertTrue(form.data['name'] == 'ok')

    def test_validate_bad_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assertTrue(not form.validate())
        self.assertTrue(form.is_validated)
        self.assertTrue(form.is_error('name'))

        self.assertTrue(form.errors_for('name') == ['Please enter a value'])

    def test_foreach_with_validators_and_multidict(self):
        from formencode import ForEach
        from pyramid_simpleform import Form
        from webob.multidict import MultiDict

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = MultiDict([
            ("name", "1"),
            ("name", "2"),
            ("name", "3"),
        ])

        form = Form(request,
                    validators=dict(name=ForEach(validators.NotEmpty())))
        self.assertTrue(form.validate())
        if hasattr(self, 'assertListEqual'):
            assertfn = self.assertListEqual
        else:
            assertfn = self.assertEqual

        assertfn(form.data["name"], ["1", "2", "3"])

    def test_is_validated_on_post(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)

        self.assertTrue(not(form.validate()))
        self.assertTrue(form.is_validated)

    def test_is_validated_with_specified_params(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)
        form.validate(params={'name' : 'foo'})
        obj = form.bind(SimpleObj())
        self.assertTrue(obj.name == 'foo')
 
    def test_bind(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleFESchema)
        form.validate()
        obj = form.bind(SimpleObj())
        self.assertTrue(obj.name == 'test')

    def test_bind_ignore_underscores(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'
        request.POST['_ignoreme'] = 'test'

        class SimpleObjWithPrivate(SimpleObj):
            _ignoreme = None

        class SimpleFESchemaWithPrivate(SimpleFESchema):
            _ignoreme = validators.String()

        form = Form(request, SimpleFESchemaWithPrivate)
        form.validate()
        obj = form.bind(SimpleObjWithPrivate())
        self.assertTrue(obj.name == 'test')
        self.assertTrue(obj._ignoreme is None)
        
    def test_bind_not_validated_yet(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleFESchema)
        self.assertRaises(RuntimeError, form.bind, SimpleObj())
 
    def test_bind_with_errors(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = ''

        form = Form(request, SimpleFESchema)
        self.assertTrue(not form.validate())
        self.assertRaises(RuntimeError, form.bind, SimpleObj())

    def test_bind_with_exclude(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleFESchema)
        form.validate()
        obj = form.bind(SimpleObj(), exclude=["name"])
        self.assertTrue(obj.name == None)
 
    def test_bind_with_include(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleFESchema)
        form.validate()
        obj = form.bind(SimpleObj(), include=['foo'])
        self.assertTrue(obj.name == None)
 
    def test_initialize_with_obj(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, obj=SimpleObj(name='test'))

        self.assertTrue(form.data['name'] == 'test')

    def test_initialize_with_defaults(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={'name' : 'test'})

        self.assertTrue(form.data['name'] == 'test')

    def test_initialize_with_obj_and_defaults(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, 
                    obj=SimpleObj(name='test1'),
                    defaults={'name' : 'test2'})

        self.assertTrue(form.data['name'] == 'test1')

    def test_variable_decode(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.POST['names-1'] = 'test1'
        request.POST['names-2'] = 'test2'
        request.method = "POST"

        form = Form(request, SimpleFESchema,
                    variable_decode=True)

        self.assertTrue(form.validate())
        self.assertEqual(form.data['name'], 'test')
        self.assertEqual(form.data['names'], ['test1', 'test2'])

    def test_variable_decode_with_error(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = ''
        request.POST['names-1'] = 'test1'
        request.POST['names-2'] = 'test2'
        request.method = "POST"

        form = Form(request, SimpleFESchema,
                    variable_decode=True)

        self.assertFalse(form.validate())
        self.assertEqual(form.data['name'], '')
        self.assertEqual(form.data['names'], ['test1', 'test2'])

    def test_validate_from_GET(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "GET"
        request.GET['name'] = 'test'

        form = Form(request, SimpleFESchema, method="GET")

        self.assertTrue(form.validate())
        self.assertTrue(form.is_validated)

    def test_validate_from_GET_if_on_POST(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "GET"
        request.GET['name'] = 'test'

        form = Form(request, SimpleFESchema)

        self.assertTrue(not form.validate())
        self.assertTrue(not form.is_validated)


    def test_force_validate(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.GET['name'] = 'test'

        form = Form(request, SimpleFESchema)

        self.assertTrue(form.validate(force_validate=True))
        self.assertTrue(form.is_validated)
 
    def test_render_without_htmlfill(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.method = "POST"
        
        settings = {}

        settings['mako.directories'] = 'pyramid_simpleform:templates'
        config = testing.setUp(settings=settings)
        config.include('pyramid_mako')


        request.registry = config.registry

        form = Form(request, SimpleFESchema)

        result = form.render("test_form.mako", htmlfill=False)
        self.assertTrue('<input type="text" name="name" size="20">' 
                     in result)


    def test_render_with_htmlfill(self):

        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.method = "POST"
        
        settings = {}

        settings['mako.directories'] = 'pyramid_simpleform:templates'
        config = testing.setUp(settings=settings)
        config.include('pyramid_mako')


        request.registry = config.registry

        form = Form(request, SimpleFESchema, defaults={'name': 'foo'})

        result = form.render("test_form.mako", htmlfill=True)
        self.assertTrue('<input type="text" name="name" size="20" value="foo">'
                     in result)


    def test_htmlfill(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema,
                    defaults={"name": "testing"})

        html = """
        <form method="POST" action=".">
            <input type="text" name="name">
        </form>
        """

        html = form.htmlfill(html)
        self.assertTrue('value="testing"' in html)


class TestFormencodeFormRenderer(unittest.TestCase):
   
    def test_begin_form(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)

        self.assertTrue(renderer.begin(url="/"),
                     '<form action="/" method="post">')

    def test_end_form(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)
       
        self.assertEqual(renderer.end(), "</form>")

    def test_csrf(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)

        self.assertEqual(renderer.csrf(),
            '<input id="_csrf" name="_csrf" type="hidden" value="0123456789012345678901234567890123456789" />')
 
    def test_csrf_token(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)

        self.assertTrue(renderer.csrf_token() == \
                '<div style="display:none;"><input id="_csrf" name="_csrf" '
                'type="hidden" value="0123456789012345678901234567890123456789" /></div>')

    def test_hidden_tag_with_csrf_and_other_names(self):
        
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={'name':'foo'})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.hidden_tag('name') == \
            '<div style="display:none;"><input id="name" name="name" '
            'type="hidden" value="foo" /><input id="_csrf" name="_csrf" '
            'type="hidden" value="0123456789012345678901234567890123456789" /></div>')

    def test_hidden_tag_with_just_csrf(self):
        
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)

        self.assertTrue(renderer.hidden_tag() == \
                '<div style="display:none;"><input id="_csrf" name="_csrf" '
                'type="hidden" value="0123456789012345678901234567890123456789" /></div>')


    def test_text(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.text("name") == \
                '<input id="name" name="name" type="text" value="Fred" />')

    def test_date(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer
        import datetime

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={
            "when" : datetime.date(2014,2,1) })
        renderer = FormRenderer(form)

        self.assertTrue(renderer.date("when", date_format="%d/%m/%Y") == \
                '<input id="when" name="when" type="text" value="01/02/2014" />')

    def test_textarea(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.textarea("name") == \
                '<textarea id="name" name="name">Fred</textarea>')

    def test_hidden(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.hidden("name") == \
                '<input id="name" name="name" type="hidden" value="Fred" />')

    def test_select(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name": "Fred"})
        renderer = FormRenderer(form)

        options = [
            ("Fred", "Fred"),
            ("Barney", "Barney"),
            ("Wilma", "Wilma"),
            ("Betty", "Betty"),
        ]

        self.assertTrue(renderer.select("name", options) ==
            """<select id="name" name="name">
<option selected="selected" value="Fred">Fred</option>
<option value="Barney">Barney</option>
<option value="Wilma">Wilma</option>
<option value="Betty">Betty</option>
</select>""")

    def test_select_webhelpers1_compatible(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name": "Fred"})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.select("currency", [["$", "Dollar"], ["DKK", "Kroner"]], "$") ==
                        """<select id="currency" name="currency">
<option selected="selected" value="$">Dollar</option>
<option value="DKK">Kroner</option>
</select>""")
        self.assertTrue(renderer.select("cc", ["VISA", "MasterCard"], "MasterCard", id="cc", class_="blue") ==
                        """<select class="blue" id="cc" name="cc">
<option value="VISA">VISA</option>
<option selected="selected" value="MasterCard">MasterCard</option>
</select>""")
        self.assertTrue(renderer.select("cc", ["VISA", "MasterCard", "Discover"], ["VISA", "Discover"]) ==
                        """<select id="cc" name="cc">
<option selected="selected" value="VISA">VISA</option>
<option value="MasterCard">MasterCard</option>
<option selected="selected" value="Discover">Discover</option>
</select>""")
        self.assertTrue(renderer.select("currency",
                                        [["$", "Dollar"], ["DKK", "Kroner"]], None, prompt="Please choose ...") ==
                        """<select id="currency" name="currency">
<option selected="selected" value="">Please choose ...</option>
<option value="$">Dollar</option>
<option value="DKK">Kroner</option>
</select>""")

        try:
            if isinstance(long, type):
                self.assertTrue(renderer.select("privacy",
                                                [(1, "Private"), (2, "Semi-public"), (3, "Public")], long(3)) ==
                                """<select id="privacy" name="privacy">
<option value="1">Private</option>
<option value="2">Semi-public</option>
<option selected="selected" value="3">Public</option>
</select>""")
        except NameError:
                self.assertTrue(renderer.select("privacy", [(1, "Private"), (2, "Semi-public"), (3, "Public")], 3) ==
                                """<select id="privacy" name="privacy">
<option value="1">Private</option>
<option value="2">Semi-public</option>
<option selected="selected" value="3">Public</option>
</select>""")

        self.assertTrue(renderer.select("recipients", 
                                        [([("u1", "User1"),
                                           ("u2", "User2")], "Users"),
                                         ([("g1", "Group1"),
                                           ("g2", "Group2")], "Groups")], None) ==
                        """<select id="recipients" name="recipients">
<optgroup label="Users">
<option value="u1">User1</option>
<option value="u2">User2</option>
</optgroup>
<optgroup label="Groups">
<option value="g1">Group1</option>
<option value="g2">Group2</option>
</optgroup>
</select>""")

    def test_select_with_tuple(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name": "Fred"})
        renderer = FormRenderer(form)

        options = (
            ("Fred", "Fred"),
            Option("Barney", "Barney"),
            ("Wilma", "Wilma"),
            ("Betty", "Betty"),
        )

        self.assertTrue(renderer.select("name", options) ==
                        """<select id="name" name="name">
<option selected="selected" value="Fred">Fred</option>
<option value="Barney">Barney</option>
<option value="Wilma">Wilma</option>
<option value="Betty">Betty</option>
</select>""")

    def test_select_with_options_list(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name": "ValueFred"})
        renderer = FormRenderer(form)

        options = [
            Option(value="ValueFred", label="LabelFred"),
            Option(value="ValueBarney", label="LabelBarney"),
            Option(value="ValueWilma", label="LabelWilma"),
            Option(value="ValueBetty", label="LabelBetty"),
        ]

        self.assertTrue(renderer.select("name", options) ==
                        """<select id="name" name="name">
<option selected="selected" value="ValueFred">LabelFred</option>
<option value="ValueBarney">LabelBarney</option>
<option value="ValueWilma">LabelWilma</option>
<option value="ValueBetty">LabelBetty</option>
</select>""")

    def test_select_with_options_obj(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name": "ValueFred"})
        renderer = FormRenderer(form)

        options = Options([
            OptGroup("OptGroup", [Option(value="ValueOG", label="LabelOG")]),
            Option(value="ValueFred", label="LabelFred"),
            Option(value="ValueBarney", label="LabelBarney"),
            Option(value="ValueWilma", label="LabelWilma"),
            Option(value="ValueBetty", label="LabelBetty"),
        ])

        self.assertTrue(renderer.select("name", options) ==
                        """<select id="name" name="name">
<optgroup label="OptGroup">
<option value="ValueOG">LabelOG</option>
</optgroup>
<option selected="selected" value="ValueFred">LabelFred</option>
<option value="ValueBarney">LabelBarney</option>
<option value="ValueWilma">LabelWilma</option>
<option value="ValueBetty">LabelBetty</option>
</select>""")

    def test_file(self):
  
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)
       
        self.assertTrue(renderer.file('file') ==
                        '<input id="file" name="file" type="file" />')

    def test_password(self):
  
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)
       
        self.assertTrue(renderer.password('password') ==
                        '<input id="password" name="password" type="password" />')


    def test_radio(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name" : 'Fred'})
        renderer = FormRenderer(form)
        
        self.assertTrue(renderer.radio("name", value="Fred") == \
                     '<input checked="checked" id="name_fred" name="name" '
                     'type="radio" value="Fred" />')
        
        self.assertTrue(renderer.radio("name", value="Barney") == \
                     '<input id="name_barney" name="name" '
                     'type="radio" value="Barney" />')

    def test_submit(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)

        self.assertTrue(renderer.submit("submit", "Submit") == \
            '<input id="submit" name="submit" type="submit" value="Submit" />')

    def test_checkbox(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name" : True})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.checkbox("name") == \
            '<input checked="checked" id="name" name="name" type="checkbox" '
            'value="1" />')

    def test_checkbox_checked(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)

        self.assertTrue(renderer.checkbox("name") == \
            '<input id="name" name="name" type="checkbox" '
            'value="1" />')

        self.assertTrue(renderer.checkbox("name", checked=True) == \
            '<input checked="checked" id="name" name="name" type="checkbox" '
            'value="1" />')

    def test_checkbox_checked_with_default(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema, defaults={"name" : True})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.checkbox("name", checked=False) == \
            '<input checked="checked" id="name" name="name" type="checkbox" '
            'value="1" />')

        self.assertTrue(renderer.checkbox("name", checked=True) == \
            '<input checked="checked" id="name" name="name" type="checkbox" '
            'value="1" />')

        form = Form(request, SimpleFESchema, defaults={"name" : False})
        renderer = FormRenderer(form)

        self.assertTrue(renderer.checkbox("name", checked=False) == \
            '<input id="name" name="name" type="checkbox" '
            'value="1" />')

        self.assertTrue(renderer.checkbox("name", checked=True) == \
            '<input id="name" name="name" type="checkbox" '
            'value="1" />')

    def test_is_error(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)

        self.assertTrue(not(form.validate()))

        renderer = FormRenderer(form)
        self.assertTrue(renderer.is_error('name'))

    def test_errors_for(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)

        self.assertTrue(not(form.validate()))
        renderer = FormRenderer(form)

        self.assertTrue(renderer.errors_for('name') == ['Missing value'])

    def test_errorlist(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assertTrue(renderer.errorlist() == \
                     '<ul class="error"><li>Missing value</li></ul>')
     

    def test_errorlist_with_no_errors(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleFESchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assertTrue(renderer.errorlist() == '')

    def test_errorlist_with_custom_localizer(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform import State
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        state = State(_=lambda s: s.upper())

        form = Form(request, SimpleFESchema, state=state)
        form.validate()

        renderer = FormRenderer(form)

        self.assertEqual(renderer.errorlist('name'),
                     '<ul class="error"><li>MISSING VALUE</li></ul>')
 
    def test_errorlist_with_field(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleFESchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assertEqual(renderer.errorlist('name'),
                     '<ul class="error"><li>Missing value</li></ul>')

    def test_label(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)
       
        self.assertTrue(renderer.label("name") == \
                   '<label for="name">Name</label>') 

    def test_label_using_field_name(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleFESchema)
        renderer = FormRenderer(form)
       
        self.assertTrue(renderer.label("name", "Your name") == \
                   '<label for="name">Your name</label>') 

