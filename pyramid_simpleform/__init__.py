from formencode import htmlfill
from formencode import variabledecode
from formencode import Invalid

from pyramid.i18n import get_localizer, TranslationStringFactory, TranslationString
from pyramid.renderers import render

try:
    _text = basestring
except NameError:
    _text = str


class State(object):
    """
    Default "empty" state object.

    Keyword arguments are automatically bound to properties, for
    example::

        obj = State(foo="bar")
        obj.foo == "bar"
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __contains__(self, k):
        return hasattr(self, k)

    def __getitem__(self, k):
        try:
            return getattr(self, k)
        except AttributeError:
            raise KeyError

    def __setitem__(self, k, v):
        setattr(self, k, v)

    def get(self, k, default=None):
        return getattr(self, k, default)

fe_tsf = TranslationStringFactory('FormEncode')


def get_default_translate_fn(request):
    pyramid_translate = get_localizer(request).translate

    def translate(s):
        if not isinstance(s, TranslationString):
            s = fe_tsf(s)

        return pyramid_translate(s)

    return translate


class Form(object):

    """
    Legacy class for validating FormEncode schemas and validators.

    `request` : Pyramid request instance

    `schema`  : FormEncode Schema class or instance

    `validators` : a dict of FormEncode validators i.e. { field : validator }

    `defaults`   : a dict of default values

    `obj`        : instance of an object (e.g. SQLAlchemy model)

    `state`      : state passed to FormEncode validators.

    `method`        : HTTP method

    `variable_decode` : will decode dict/lists

    `dict_char`       : variabledecode dict char

    `list_char`       : variabledecode list char

    Also note that values of ``obj`` supercede those of ``defaults``. Only
    fields specified in your schema or validators will be taken from the 
    object.
    """

    default_state = State

    def __init__(self, request, schema=None, validators=None, defaults=None, 
                 obj=None, extra=None, include=None, exclude=None, state=None, 
                 method="POST", variable_decode=False,  dict_char=".", 
                 list_char="-", multipart=False):

        self.request = request
        self.schema = schema
        self.validators = validators or {}
        self.method = method
        self.variable_decode = variable_decode
        self.dict_char = dict_char
        self.list_char = list_char
        self.multipart = multipart
        self.state = state

        self.is_validated = False

        self.errors = {}
        self.data = {}

        if self.state is None:
            self.state = self.default_state()

        if not hasattr(self.state, '_'):
            self.state._ = get_default_translate_fn(request)

        if defaults:
            self.data.update(defaults)

        if obj:
            fields = list(self.schema.fields.keys()) + list(self.validators.keys())
            for f in fields:
                if hasattr(obj, f):
                    self.data[f] = getattr(obj, f)

    def is_error(self, field):
        """
        Checks if individual field has errors.
        """
        return field in self.errors

    def all_errors(self):
        """
        Returns all errors in a single list.
        """
        if isinstance(self.errors, _text):
            return [self.errors]
        if isinstance(self.errors, list):
            return self.errors
        errors = []
        try:
            iter_keys = self.errors.iterkeys()
        except AttributeError:
            iter_keys = self.errors.keys()

        for field in iter_keys:
            errors += self.errors_for(field)
        return errors

    def errors_for(self, field):
        """
        Returns any errors for a given field as a list.
        """
        errors = self.errors.get(field, [])
        if isinstance(errors, _text):
            errors = [errors]
        return errors

    def validate(self, force_validate=False, params=None):
        """
        Runs validation and returns True/False whether form is 
        valid.
        
        This will check if the form should be validated (i.e. the
        request method matches) and the schema/validators validate.

        Validation will only be run once; subsequent calls to 
        validate() will have no effect, i.e. will just return
        the original result.

        The errors and data values will be updated accordingly.

        `force_validate`  : will run validation regardless of request method.

        `params`          : dict or MultiDict of params. By default 
        will use **request.json_body** (if JSON body), **request.POST** (if HTTP POST) or **request.params**.
        """

        assert self.schema or self.validators, \
                "validators and/or schema required"

        if self.is_validated:
            return not(self.errors)

        if not force_validate:
            if self.method and self.method != self.request.method:
                return False

        try:
            json_body = self.request.json_body
        except AttributeError:
            json_body = None
        if params is None:
            if json_body:
                params = json_body
            elif self.method == "POST":
                params = self.request.POST
            else:
                params = self.request.params
            
        if self.variable_decode and not json_body:
            decoded = variabledecode.variable_decode(
                        params, self.dict_char, self.list_char)

        else:
            decoded = params
        if hasattr(decoded, "mixed"):
            decoded = decoded.mixed()

        self.data.update(decoded)

        if self.schema:
            try:
                self.data = self.schema.to_python(decoded, self.state)
            except Invalid as e:
                self.errors = e.unpack_errors(self.variable_decode,
                                              self.dict_char,
                                              self.list_char)

        if self.validators:
            try:
                iter_items = self.validators.iteritems()
            except AttributeError:
                iter_items = self.validators.items()

            for field, validator in iter_items:
                try:
                    self.data[field] = validator.to_python(decoded.get(field),
                                                           self.state)

                except Invalid as e:
                    try:
                        self.errors[field] = unicode(e)
                    except NameError:
                        self.errors[field] = str(e)


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

        Note that any properties starting with underscore "_" are ignored
        regardless of ``include`` and ``exclude``. If you need to set these
        do so manually from the ``data`` property of the form instance.

        Calling bind() before running validate() will result in a RuntimeError
        """

        if not self.is_validated:
            raise RuntimeError("Form has not been validated. Call validate() first")

        if self.errors:
            raise RuntimeError("Cannot bind to object if form has errors")

        items = [(k, v) for k, v in self.data.items() if not k.startswith("_")]
        for k, v in items:

            if include and k not in include:
                continue

            if exclude and k in exclude:
                continue

            setattr(obj, k, v)

        return obj

    def htmlfill(self, content, **htmlfill_kwargs):
        """
        Runs FormEncode **htmlfill** on content.
        """

        charset = getattr(self.request, 'charset', 'utf-8')
        htmlfill_kwargs.setdefault('encoding', charset)
        return htmlfill.render(content, 
                               defaults=self.data,
                               errors=self.errors,
                               **htmlfill_kwargs)

    def render(self, template, extra_info=None, htmlfill=True,
              **htmlfill_kwargs):
        """
        Renders the form directly to a template,
        using Pyramid's **render** function. 

        `template` : name of template

        `extra_info` : dict of extra data to pass to template

        `htmlfill` : run htmlfill on the result.

        By default the form itself will be passed in as `form`.

        htmlfill is automatically run on the result of render if
        `htmlfill` is **True**.

        This is useful if you want to use htmlfill on a form,
        but still return a dict from a view. For example::

            @view_config(name='submit', request_method='POST')
            def submit(request):

                form = Form(request, MySchema)
                if form.validate():
                    # do something
                return dict(form=form.render("my_form.html"))

        """
        
        extra_info = extra_info or {}
        extra_info.setdefault('form', self)

        result = render(template, extra_info, self.request)
        if htmlfill:
            result = self.htmlfill(result, **htmlfill_kwargs)
        return result
