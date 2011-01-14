pyramid_simpleform
==================

**pyramid_simpleform** provides some simple helper classes for managing your forms in a Pyramid project. It uses FormEncode and WebHelpers for most of the heavy lifting, so if you're familiar with these most of this will be familiar to you. It doesn't require any special setup or ZCML voodoo and is template-agnostic.

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

    from pyramid_simpleform import Form

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

        return dict(form=form.get_renderer())


The code is very simple. The **Form** instance is initialized with the request and your schema - it can be a **Schema** class or instance. The **validate** method does two things. First, it checks if the form should be validated (more of which in a moment) and if so it does the validation. It just returns a simple **True** or **False** depending on whether you are OK to continue or not. You can then access the validated data directly through the **data** property. If validation fails, the errors are dumped into the **errors** property.

If validation hasn't yet happened, or if the form contains errors, you want to display the template with the form. We pass that into the template the usual way, but notice that instead of passing the form directly, we call **form.get_renderer()**. This returns an object whose job it is to do the actual rendering of all the bits of HTML that show the form to the user. Here's ``submit.html`` (using Jinja2 syntax)::

    {{ form.begin(".") }}
    <div style="display:none;">
        {{ form.csrf() }}
    </div>
    <div>
        {% if form.is_errors("title") %}
        <ul class="errors">
            {% for error in form.errors_for("title") %}
            <li>{{ error }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {{ form.label("title") }}
        {{ form.text("title", size=40) }}
    </div>
    <div>
        {{ form.label("content") }}
        {{ form.textarea("content", rows=5, cols=40) }}
    </div>
    <div>
        {{ form.submit("submit", "Publish") }}
    </div>
    {{ form.end() }}

As you can see, a lot of layout and rendering control is ceded to the template. That's intentional. Some form libraries let you do this::

    {{ form.render() }}

which renders the entire thing, all the **div** tags and all. However managing this is far from simple. What if you want paragraphs or list items instead ? Where do you store the templates ? What if your designer wants you to break the form up into separate columns, or you need some fancy JavaScript effects on the side ? The easiest place to do all of that is in the template. The renderer simply makes it easy to output the little form widgets for you. If you have lots of repetitive markup (for example rendering errors) the best solution is to use a Mako/Jinja2 macro, or whatever your template engine of choice supports. 

Notice this line::

    {{ form.csrf() }}

This renders a hidden CSRF widget that helps you keep your users safe. We'll come back to that later.

CSRF validation
---------------

The default **FormRenderer** also has a method **csrf()** which renders a hidden input with a fresh CSRF token. This is reset with each request. You have to include this in your form for this to work.

This will create a new CSRF token if one is not already assigned, using Pyramid's underlying CSRF functionality.

There is also a convenience method **csrf_token()** which will render the CSRF input inside a hidden DIV, in order to maintain valid markup.

It's up to you to ensure that your form does proper CSRF validation. One suggestion is to create an event to do this automatically with all non-AJAX POST requests::

    # in your subscribers.py

    def csrf_validation(request):

        if request.method == "POST" and not request.is_xhr:

            token = request.POST.get("_csrf")
            if not token or token != request.session.get_csrf_token():
                raise HTTPForbidden, "CSRF token is invalid or missing"

    # in your main() function

    config.add_subscriber("myapp.subscribers.csrf_validation", 
                          event=NewRequest)


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
    
    return dict(form=form.get_renderer())
 
You can pass a couple of arguments, ``include`` and ``exclude`` to **bind()** to filter out any fields you explicitly don't want bound. This can of course be done in the schema using **filter_extra_fields** but sometimes it pays to be extra careful. For example, you don't
want the "date_created" field to be overriden in the form::

    post = form.bind(BlogPost(), exclude=["date_created"])

If you try to call **bind()** before running **validate()**, or if your form has errors, it will blow up with a **RuntimeError**.

Custom renderers
----------------

The default **FormRenderer** should cover most cases, but you might want to do something a bit different - for example, adding some HTML5-specific widgets. To do this, first create your own renderer class::

    from pyramid_simpleform import FormRenderer

    class HTML5FormRenderer(FormRenderer):

        def date(self, name, value=None, id=None, **attrs):
            return self.input('search', name, value, id, **attrs)


Then just set the **renderer_class** property of the form::

    form = Form(request, BlogPostSchema, renderer_class=HTML5FormRenderer)


