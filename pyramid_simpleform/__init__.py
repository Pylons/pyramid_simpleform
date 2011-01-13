import webhelpers.html.tags as h

from webhelpers.html.builder import HTML

from formencode import variabledecode
from formencode import Invalid

from pyramid.httpexceptions import HTTPForbidden

__all__ = ["Form", "FormRenderer"]

class Form(object):

    """
    `request` : Pyramid request instance

    `schema`  : FormEncode Schema class or instance
    `validators` : a dict of FormEncode validators i.e. { field : validator }

    `defaults`   : a dict of default values
    `obj`        : instance of an object (e.g. SQLAlchemy model)
    `state`      : state passed to FormEncode validators. If not present then 
                   `obj` is passed instead

    `method`        : HTTP method
    `validate_csrf` : CSRF validation will be run. Raises HTTPForbidden if fails.

    `variable_decode` : will decode dict/lists
    `dict_char`       : variabledecode dict char
    `list_char`       : variabledecode list char

    `renderer_class`  : class used to render the form. Uses FormRenderer by default.
    """

    def __init__(self, request, schema=None, validators=None, defaults=None, 
                 obj=None, state=None, method="POST", validate_csrf=True,
                 variable_decode=True, dict_char=".", list_char="-",
                 multipart=False, renderer_class=None):

        self.request = request
        self.schema = schema
        self.validators = None
        self.method = method
        self.variable_decode = variable_decode
        self.dict_char = dict_char
        self.list_char = list_char
        self.validate_csrf = validate_csrf
        self.multipart = multipart

        self.is_validated = False

        self.errors = {}
        self.data = {}

        self.renderer_class = renderer_class or FormRenderer
        
        if defaults:
            self.data.update(defaults)

        if obj:
            self.data.update(obj.__dict__)
            if state is None:
                state = obj

        self.state = state

        assert self.schema or self.validators, \
                "validators and/or schema required"

    def get_renderer(self):
        """
        Returns a renderer instance based on renderer_class.
        """
        return self.renderer_class(self)

    def is_error(self, field):
        """
        Checks if individual field has errors.
        """
        return field is self.errors

    def errors_for(self, field):
        """
        Returns any errors for a given field as a list.
        """
        errors = self.errors.get(field, [])
        if isinstance(errors, basestring):
            errors = [errors]
        return errors

    def validate(self):
        """
        Runs validation and returns True/False whether form is 
        valid.
        
        This will check if the form should be validated (i.e. the
        request method matches) and the schema/validators validate.

        Will also check CSRF if validate_csrf is True.

        Validation will only be run once; subsequent calls to 
        validate() will have no effect, i.e. will just return
        the original result.

        The errors and data values will be updated accordingly.

        """

        if self.is_validated:
            return not(self.errors)

        if self.method and self.method != self.request.method:
            return False

        if self.method == "POST":
            params = self.request.POST
        else:
            params = self.request.params
        
        if self.validate_csrf:
            value = params.pop("_csrf", None)
            if not value or value != self.request.session.get_csrf_token():
                raise HTTPForbidden, "CSRF token is missing"

        if self.variable_decode:
            decoded = variabledecode.variable_decode(
                        params, self.dict_char, self.list_char)

        else:
            decoded = params

        self.data.update(params)

        if self.schema:
            try:
                self.data = self.schema.to_python(decoded, self.state)
            except Invalid, e:
                self.errors = e.unpack_errors(self.variable_decode,
                                              self.dict_char,
                                              self.list_char)


        if self.validators:
            for field, validator in self.validators.iteritems():
                try:
                    self.data[field] = validator.to_python(decoded.get(field),
                                                           self.state)

                except Invalid, e:
                    self.errors[field] = e

        self.is_validated = True

        return not(self.errors)

    def bind(self, obj, include=None, exclude=None):
        """
        Binds validated field values to an object instance, for example a
        SQLAlchemy model instance.

        `include` : list of included fields. If field not in this list it 
                    will not be bound to this object.
        `exclude` : list of excluded fields. If field is in this list it 
                    will not be bound to the object.

        Returns the `obj` passed in.

        Calling bind() before running validate() will result in a RuntimeError
        """

        if not self.is_validated:
            raise RuntimeError, \
                    "Form has not been validated. Call validate() first"

        if self.errors:
            raise RuntimeError, "Cannot bind to object if form has errors"

        for k, v in self.data.items():

            if include and k not in include:
                continue

            if exclude and k in exclude:
                continue

            setattr(obj, k, v)

        return obj


class FormRenderer(object):
    """
    A simple form renderer class. Uses webhelpers to render individual
    form fields.
    """

    def __init__(self, form):

        self.form = form
        self.request = self.form.request
        self.data = self.form.data
        self.errors = self.form.errors
        self.multipart = self.form.multipart

    def value(self, name, default=None):
        return self.data.get(name, default)

    def begin(self, action, **attrs):
        """
        Creates the opening <form> tags.
        """
        return h.form(action, multipart=self.multipart, **attrs)

    def end(self):
        """
        Closes the form.
        """
        return h.end_form()
    
    def csrf(self):
        """
        Returns the CSRF hidden tag
        """
        value = self.request.session.new_csrf_token()
        return self.hidden("_csrf", value=value)

    def text(self, name, value=None, id=None, **attrs):
        return h.text(name, self.value(name, value), id, **attrs)

    def file(self, name, value=None, id=None, **attrs):
        return h.file(name, self.value(name, value), id, **attrs)

    def hidden(self, name, value=None, id=None, **attrs):
        return h.hidden(name, self.value(name, value), id, **attrs)

    def radio(self, name, value=None, checked=False, label=None, **attrs):
        checked = self.data.get(name) == value or checked
        return h.radio(name, self.value(name, value), checked, label, **attrs)

    def submit(self, name, value=None, id=None, **attrs):
        return h.submit(name, self.value(name, value), id, **attrs)

    def select(self, name, options, selected_value=None, id=None, **attrs):
        return h.select(name, self.value(name, selected_value), 
                        options, id, **attrs)

    def checkbox(self, name, value="1", checked=False, label=None, id=None, 
                 **attrs):
    
        return h.checkbox(name, value, self.value(name), label, id, **attrs)

    def textarea(self, name, content="", id=None, **attrs):
        return h.textarea(name, self.value(name, content), id, attrs)

    def password(self, name, value=None, id=None, **attrs):
        return h.password(name, self.value(name, value), id, attrs)

    def label(self, name, label=None, **attrs):
        if 'for_' not in attrs:
            attrs['for_'] = name
        label = label or name.capitalize()
        return HTML.tag("label", label, **attrs)
        
    def is_error(self, name):
        return self.form.is_error(name)

    def errors_for(self, name):
        return self.form.errors_for(name)



