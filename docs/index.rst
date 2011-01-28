pyramid_simpleform
==================

**pyramid_simpleform**, as the name implies, is a simple form validation and rendering library. It's intended to replace the old ``@validate`` decorator from Pylons with a form handling pattern inspired by `Django forms`_, `WTForms`_ and `Flatland`_. However it's also intended for use with the `Pyramid`_ framework and uses `FormEncode`_ for most of the heavy lifting. It's therefore assumed you are already familiar with FormEncode.

Installation
------------

Install using **pip install pyramid_simpleform** or **easy_install pyramid_simpleform**.

If installing from source, untar/unzip, cd into the directory and do **python setup.py install**.

The source repository is on `Bitbucket`_. Please report any bugs, issues or queries there. 

Getting started
---------------

**pyramid_simpleform** doesn't require any special configuration using ZCML or otherwise. You just create FormEncode schemas or validators for your application as usual, and wrap them in a special **Form** class. The **Form** provides a number of helper methods to make form handling as painless, and still flexible, as possible.

Here is a typical example::

    from pyramid.view import view_config
    from validators import Schema, validators

    from pyramid_simpleform import Form
    from pyramid_simpleform.renderers import FormRenderer

    class MyModelSchema(Schema):

        filter_extra_fields = True
        allow_extra_fields = True

        name = validators.MinLength(5, not_empty=True)
        value = validators.Int(not_empty=True)

    class MyModel(object):

        pass


    @view_config(renderer='edit.html')
    def edit(self):

        item_id = self.request.matchdict['item_id']
        item = session.query(MyModel).get(item_id)

        form = Form(self.request, 
                    schema=MyModelSchema, 
                    obj=item)

        if form.validate():
            
            form.bind(item)
           
            # persist model somewhere...
            return HTTPFound(location="/")

        return dict(item=item, form=FormRenderer(form))


    @view_config(renderer='submit.html')
    def submit(self):
        
        form = Form(self.request, 
                    defaults={"name" : "..."})
                    schema=MyModelSchema)

        if form.validate():

            obj = form.bind(MyModel())

            # persist model somewhere...

            return HTTPFound(location="/")

    return dict(renderer=FormRenderer(form))


In your template (using `Jinja2`_ in this example)::

    {{ renderer.begin(route_url("submit")) }}
    {{ renderer.csrf_token() }}
    <div class="field">
        {{ renderer.errorlist("name") }}
        {{ renderer.text("name", size=30)
    </div>
    ....
    <div class="buttons">
        {{ renderer.submit("submit", "Submit") }}
    </div>
    {{ renderer.end() }}

The steps are:

1. Create a **Form** instance with a Request and your schema and/or validators. You can optionally pass in default values or an object instance. 

2. Call **validate()**. This will check if the form should be validated (in most cases, if the request method is HTTP POST), and validates against the provided schema. It returns **True** if the form has been validated and there are no errors. Any errors get dumped into the **errors** property as a dict. 

3. If the form is valid, use **bind()** to bind the form fields to your object. If you would rather do this manually (or you don't have an object) you can access the validated data (as a dict) from the **data** property of the form.

4. If the form hasn't been validated yet, or contains errors, pass it to your template. The form can optionally be wrapped in a **FormRenderer** which makes it easier to output individual HTML widgets.

Validation
----------

The **validate()** method does two things. First, it checks if the form should be validated. Second, it performs the validation against your schema or validators. 

By default, validation will run if the request method is HTTP POST. This is set by the `method` argument to the constructor.

The validated values, or values from the request, are passed to the **data** property. Any errors are passed to the **errors** property.

Working with models
-------------------

**pyramid_simpleform** makes it easier to work with your models (be they SQLAlchemy or ZODB models, or something else).

First, you can pass the `obj` argument to the constructor, which can be used instead of `defaults` to set default values in your form::

    form = Form(request, MyModelSchema, obj=MyModel(name="foo"))
    assert form.data['name'] == 'foo'

Second, the **bind()** method sets object properties from your form fields::

    if form.validate():
        
        obj = form.bind(MyModel())


Some care should be taken when using **bind()**. You should ensure that your schema uses **filter_extra_fields** to remove any unused form fields (perhaps added by a malicious user) from the data. You can also use the parameters **include** and **exclude** to filter any unwanted data::

    if form.validate():
        obj = form.bind(MyModel(), include=['name', 'value'])

Note that running **bind()** on a form that hasn't been validated yet, or where the form contains errors, will raise a **RuntimeError**.

Form rendering
--------------

Form rendering can be done completely manually if you wish, or using webhelpers, template macros, or other methods. The **FormRenderer** class contains some useful helper methods for outputting common form elements. It uses the `WebHelpers`_ library under the hood.

The widget methods automatically bind to the relevant field in the parent **Form** class. For example::

    form = Form(request, MySchema, defaults={"name" : "foo"})
    renderer = FormRenderer(form)

If this is output using the **text()** method of your renderer::

    {{ renderer.text("name", size=30) }}

will result in this HTML snippet::

    <input type="text" name="name" id="name" value="foo" size="30" />

The **Form** class also comes with an **htmlfill()** method which uses `FormEncode`_ **htmlfill** to render errors and defaults.

CSRF Validation
---------------

**pyramid_simpleform** doesn't do CSRF validation: this is left up to you. One useful pattern is to use a **NewRequest** event to handle CSRF validation automatically::

    def csrf_validation(event):

        if event.request.method == "POST" and not event.request.is_xhr:
            
            token = event.request.POST.get("_csrf")
            if token is None or token != event.request.session.get_csrf_token():
                raise HTTPForbidden, "CSRF token is missing or invalid"

However the **FormRenderer** class has a couple of helper methods for rendering the CSRF hidden input. **csrf()** just prints the input tag, while **csrf_token()** wraps the input in a hidden DIV to keep your markup valid.

Remember to use the **allow_extra_fields** option with your schema to prevent validation errors caused by having the "_csrf" value (or other field values) in your form. A good tip is to create a base Schema class with **allow_extra_fields** and **filter_extra_fields** set to **True** and subclass this base Schema class with all your other schemas.

API
---

.. module:: pyramid_simpleform

.. autoclass:: Form
   :members:
    
.. module:: pyramid_simpleform.renderers

.. autoclass:: FormRenderer
   :members:


.. _Bitbucket: http://bitbucket.org/danjac/pyramid_simpleform
.. _Django forms: http://docs.djangoproject.com/en/dev/topics/forms/
.. _WTForms: http://pypi.python.org/pypi/WTForms/
.. _Flatland: http://pypi.python.org/pypi/flatland/
.. _Jinja2: http://pypi.python.org/pypi/Jinja2/
.. _FormEncode: http://pypi.python.org/pypi/FormEncode/
.. _Pyramid: http://pypi.python.org/pypi/pyramid/
.. _WebHelpers: http://pypi.python.org/pypi/WebHelpers/
