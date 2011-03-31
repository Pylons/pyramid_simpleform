pyramid_simpleform
==================

**pyramid_simpleform**, as the name implies, is a simple form validation and rendering library. It's intended to replace the old ``@validate`` decorator from Pylons with a form handling pattern inspired by `Django forms`_, `WTForms`_ and `Flatland`_. However it's also intended for use with the `Pyramid`_ framework and uses `Colander`_ for most of the heavy lifting. It's therefore assumed you are already familiar with Colander.

**PLEASE NOTE**

**pyramid_simpleform** was originally designed to use with FormEncode. FormEncode usage is being deprecated in favour of Colander as of version **0.7**, as FormEncode itself is no longer actively maintained and Colander is used by other libraries in the Pyramid ecosystem, such as `Deform`_.

It is therefore recommended if possible that you migrate existing FormEncode schemas over to Colander. 


Installation
------------

Install using **pip install pyramid_simpleform** or **easy_install pyramid_simpleform**.

If installing from source, untar/unzip, cd into the directory and do **python setup.py install**.

The source repository is on `Bitbucket`_. Please report any bugs, issues or queries there. 

Getting started
---------------

**pyramid_simpleform** doesn't require any special configuration using ZCML or otherwise. You just create FormEncode schemas or validators for your application as usual, and wrap them in a special **Form** class. The **Form** provides a number of helper methods to make form handling as painless, and still flexible, as possible.

Here is a typical (truncated) example::

    import colander

    from pyramid.view import view_config

    from pyramid_simpleform.form import Form
    from pyramid_simpleform.renderers import FormRenderer

    class MyModelSchema(colander.MappingSchema):

        name = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(5)
        )

        value = colander.SchemaNode(colander.Int())

    class MyModel(object):
        """
        Mock object. 
        """

        pass


    @view_config(name='edit',
                 renderer='edit.html')
    def edit(self):

        item_id = request.matchdict['item_id']
        item = session.query(MyModel).get(item_id)

        form = Form(request, 
                    schema=MyModelSchema(), 
                    obj=item)

        if form.validate():
            
            form.bind(item)
           
            # persist model somewhere...
            return HTTPFound(location="/")

        return dict(item=item, form=FormRenderer(form))


    @view_config(name='add',
                 renderer='submit.html')
    def add(self):
        
        form = Form(request, 
                    defaults={"name" : "..."},
                    schema=MyModelSchema())

        if form.validate():

            obj = form.bind(MyModel())

            # persist model somewhere...

            return HTTPFound(location="/")

        return dict(renderer=FormRenderer(form))


In your template (using a Mako template in this example)::

    ${renderer.begin(request.resource_url(request.root, 'add'))}
    ${renderer.csrf_token()}
    <div class="field">
        ${renderer.errorlist("name")}
        ${renderer.text("name", size=30)}
    </div>
    ....
    <div class="buttons">
        ${renderer.submit("submit", "Submit")}
    </div>
    ${renderer.end()}

The steps are:


1. Create a **Form** instance with the Request and your schema. You can optionally pass in default values or an object instance. 

2. Call **validate()**. This will check if the form should be validated (in most cases, if the request method is HTTP POST), and validates against the provided schema. It returns **True** if the form has been validated and there are no errors. Any errors get dumped into the **errors** property as a dict. 

3. If the form is valid, use **bind()** to bind the form fields to your object. If you would rather do this manually (or you don't have an object) you can access the validated data (as a dict) from the **data** property of the form.

4. If the form hasn't been validated yet, or contains errors, pass it to your template. The form can optionally be wrapped in a **FormRenderer** which makes it easier to output individual HTML widgets.

For a complete working example, look at the "examples" directory in the source repository.

Validation
----------

The **validate()** method does two things. First, it checks if the form should be validated. Second, it performs the validation against your schema or validators. 

By default, validation will run if the request method is HTTP POST. This is set by the `method` argument to the constructor.

The validated values, or values from the request, are passed to the **data** property. Any errors are passed to the **errors** property.

Working with models
-------------------

**pyramid_simpleform** makes it easier to work with your models (be they SQLAlchemy or ZODB models, or something else).

First, you can pass the `obj` argument to the constructor, which can be used instead of `defaults` to set default values in your form::

    form = Form(request, MyModelSchema(), obj=MyModel(name="foo"))
    assert form.data['name'] == 'foo'

Second, the **bind()** method sets object properties from your form fields::

    if form.validate():
        
        obj = form.bind(MyModel())


Some care should be taken when using **bind()**. You can use the parameters **include** and **exclude** to filter any unwanted data::

    if form.validate():
        obj = form.bind(MyModel(), include=['name', 'value'])

Note that running **bind()** on a form that hasn't been validated yet, or where the form contains errors, will raise a **RuntimeError**.

Also note that attributes starting with an underscore will not be explicitly bound. In order to bind such properties you must do so manually from the ``data`` property of your form instance.

Form rendering
--------------

Form rendering can be done completely manually if you wish, or using webhelpers, template macros, or other methods. The **FormRenderer** class contains some useful helper methods for outputting common form elements. It uses the `WebHelpers`_ library under the hood.

The widget methods automatically bind to the relevant field in the parent **Form** class. For example::

    form = Form(request, MySchema(), defaults={"name" : "foo"})
    renderer = FormRenderer(form)

If this is output using the **text()** method of your renderer::

    ${renderer.text("name", size=30)}

will result in this HTML snippet::

    <input type="text" name="name" id="name" value="foo" size="30" />

It is expected that you will want to subclass **FormRenderer**, for example you might wish to generate custom fields with JavaScript, HTML5 fields, and so on.


Peppercorn
----------

**pyramid_simpleform** has optional support for the `Peppercorn`_ library, which is used for more advanced serialization/deserialization of web input. 

The **FormRenderer** class supports the creation of the special `__start__` and `__end__` hidden tags required by Peppercorn::

    renderer = FormRenderer(form)
    renderer.start_hidden_tag('mapping', 'series')
    >>> <<div style="display:none;">input type="hidden" name="__start__" value="series:mapping" /></div>

    renderer.end_hidden_tag()
    >>> <div style="display:none;"><input type="hidden" name="__end__" /></div>

    renderer_end_hidden_tags(3)
    >>> <div style="display:none;"><input type="hidden" name="__end__" /><input type="hidden" name="__end__" /><input type="hidden" name="__end__" /></div>

Note that the hidden tags are automatically wrapped in hidden DIVs to preserve valid markup.

The parameters are automatically passed through the Peppercorn ``parse`` function. 

See the `Peppercorn`_ docs for more information.


CSRF Validation
---------------

**pyramid_simpleform** doesn't do CSRF validation: this is left up to you. One useful pattern is to use a **NewRequest** event to handle CSRF validation automatically::

    def csrf_validation(event):

        if event.request.method == "POST":
            
            token = event.request.POST.get("_csrf")
            if token is None or token != event.request.session.get_csrf_token():
                raise HTTPForbidden, "CSRF token is missing or invalid"

However the **FormRenderer** class has a couple of helper methods for rendering the CSRF hidden input. **csrf()** just prints the input tag, while **csrf_token()** wraps the input in a hidden DIV to keep your markup valid.


Formencode
----------

**pyramid_simpleform** includes legacy support for `FormEncode`_ schemas and validators. This usage is deprecated and so will be eventually phased out, so it is recommended if possible to migrate existing FormEncode-based simpleform usage to Colander.

You can access the old FormEncode Form class directly under the **pyramid_simpleform** package::

    from pyramid_simpleform import Form

Contrast this with the new, Colander-based class::

    from pyramid_simpleform.form import Form

The FormEncode-based Form works pretty much as the new Form, except that you pass in a FormEncode schema, or a dict of validators, rather than a Colander schema::

    from formencode import Schema, validators
    from pyramid_simpleform import Form

    class MySchema(Schema):

        allow_extra_fields = True
        filter_extra_fields = True

        name = validators.String(not_empty=True)

    form = Form(request, MySchema)
    if form.validate():
        obj = form.bind(MyModel())
        # ... process as usual

It uses the same **FormRenderer** class::

    renderer = FormRenderer(form)


Note the use of the `allow_extra_fields` and `filter_extra_fields` attributes. These are recommended in order to remove unneeded fields (such as the CSRF) and also to prevent extra field values being passed through.

State
-----

The FormEncode-based Form also includes support for handling state, including i18n.
[TBD]

API
---


.. module:: pyramid_simpleform.form

.. autoclass:: Form
   :members:

.. module:: pyramid_simpleform

.. autoclass:: Form
   :members:
   
.. autoclass:: State
   :members:
    
.. module:: pyramid_simpleform.renderers

.. autoclass:: FormRenderer
   :members:


.. _Bitbucket: http://bitbucket.org/danjac/pyramid_simpleform
.. _Django forms: http://docs.djangoproject.com/en/dev/topics/forms/
.. _WTForms: http://pypi.python.org/pypi/WTForms/
.. _Flatland: http://pypi.python.org/pypi/flatland/
.. _FormEncode: http://pypi.python.org/pypi/FormEncode/
.. _Colander: http://pypi.python.org/pypi/Colander/
.. _Peppercorn: http://pypi.python.org/pypi/Peppercorn/
.. _Deform: http://pypi.python.org/pypi/Deform/
.. _Pyramid: http://pypi.python.org/pypi/pyramid/
.. _WebHelpers: http://pypi.python.org/pypi/WebHelpers/
