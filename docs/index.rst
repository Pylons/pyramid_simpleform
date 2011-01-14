pyramid_simpleform
==================

**pyramid_simpleform** provides some simple helper classes for managing your forms in a Pyramid project. It uses FormEncode and WebHelpers for most of the heavy lifting, so if you're familiar with these most of this will be familiar to you. It doesn't require any special setup or ZCML voodoo and is template-agnostic.

While **pyramid_simpleform** uses FormEncode, it has also been inspired by libraries such as Django forms, WTForms and Flatland. Unlike these libraries it's designed as a simple wrapper around existing form validation and rendering tools, and is specifically intended for use with Pyramid.

Installation
------------

Once this is in PyPi, you should be able to just do **pip install pyramid_simpleform**. For now, download the source, cd into the directory, and do **python setup.py install**.

Getting started
---------------

Once you've installed **pyramid_simpleform** you first need to create a set of **FormEncode** validators or schemas.

For example, if you're building a blog application (just to be original) you might have a "BlogPost" model. It doesn't matter whether this is a SQLAlchemy model, ZODB thingamjig or some other creation. We'll represent it here as a plain Python object::

    from datetime import datetime

    class BlogPost(object):

        def __init__(self, title=None, content=None):
            self.title = title
            self.content = content
            self.date_created = datetime.utcnow()

We want to create a simple submit view to create new blog posts. Basically, the steps are:

1. If you arrive at the page via a simple GET, render the form. 
2. If you submit (POST) the form, do validation
3. If the form is valid, enter the blog post in the database and redirect somewhere else.
4. If the form isn't valid, re-display the original form with the errors shown plus the stuff you entered.

That's pretty much what most forms have to do.

In short, this is what the view looks like. We'll skip all the other views and security stuff for the sake of clarity::


    from pyramid.view import view_config
    from pyramid.httpexceptions import HTTPFound

    from pyramid_simpleform import Form, FormRenderer

    from myapp.models import BlogPost

    class BlogPostSchema(Schema):

        allow_extra_fields = True
        filter_extra_fields = True

        title = validators.MinLength(10, not_empty=True)
        content = validators.NotEmpty()

    
    @view_config(name="submit", route_url="/submit/", renderer="submit.html")
    def submit(request):

        form = Form(request, BlogPostSchema)

        if form.validate():

            post = BlogPost(title=form.data['title']
                            content=form.data['content'])

            # do whatever db persistence you need here

            return HTTPFound(location="/")

        return dict(form=form)


The code is very simple. The **Form** instance is initialized with the request and your schema - it can be a **Schema** class or instance. The **validate** method does two things. First, it checks if the form should be validated (more of which in a moment) and if so it does the validation. It just returns a simple **True** or **False** depending on whether you are OK to continue or not. You can then access the validated data directly through the **data** property. If validation fails, the errors are dumped into the **errors** property.


Working with models
-------------------

Whatever persistence system you use, **pyramid_simpleform** helps with the drudgery of moving values to and from your form and model.

The **bind()** method sets the properties of the object from the fields in your form. For example, the above view could be rewritten as::

    @view_config(name="submit", route_url="/submit/", renderer="submit.html")
    def submit(request):

        form = Form(request, BlogPostSchema)

        if form.validate():

            post = form.bind(BlogPost())
            # do whatever db persistence you need here

            return HTTPFound(location="/")
    
    return dict(form=FormRenderer(form))
 
You can pass a couple of arguments, ``include`` and ``exclude`` to **bind()** to filter out any fields you explicitly don't want bound. This can of course be done in the schema using **filter_extra_fields** but sometimes it pays to be extra careful. For example, you don't
want the "date_created" field to be overriden in the form::

    post = form.bind(BlogPost(), exclude=["date_created"])

If you try to call **bind()** before running **validate()**, or if your form has errors, it will blow up with a **RuntimeError**.

When you create your **Form** instance you can pass in ``obj`` rather than ``defaults``. While ``defaults`` expects a dict, the ``obj`` properties will be used to automatically pre-fill your form fields::

    form = Form(request, schema=BlogPostSchema, obj=item)

CSRF validation
---------------

Form rendering
--------------

You can render your form in any way you like: the **Form** class just provides the basic wrapper. It includes however an **htmlfill()** method to wrap the output content::

    form = Form(request, BlogPostSchema)
    return form.htmlfill(render_response("submit.html", dict(form=form)))

However many people don't like htmlfill, and prefer to output default values, errors etc. manually (with the help of template macros and other helpers). 

In either case, **pyramid_simpleform** comes with a **FormRenderer** class to help you output individual widgets. It uses the WebHelpers library under the hood. 

If you need to create special widgets (e.g. new HTML5 input types) just subclass **FormRenderer**.


Custom renderers
----------------

The default **FormRenderer** should cover most cases, but you might want to do something a bit different - for example, adding some HTML5-specific widgets. To do this, first create your own renderer class::

    from pyramid_simpleform import FormRenderer

    class HTML5FormRenderer(FormRenderer):

        def date(self, name, value=None, id=None, **attrs):
            return self.input('search', name, value, id, **attrs)


Then just use this class in place of FormRenderer::

    renderer = HTML5FormRenderer(form)

Other examples of renderers might be one that uses FormEncode's **htmlfill** library, or returns JSON. These are being considered for future versions.



