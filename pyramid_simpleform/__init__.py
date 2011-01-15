from formencode import htmlfill
from formencode import variabledecode
from formencode import Invalid


class Form(object):

    """
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

    """

    def __init__(self, request, schema=None, validators=None, defaults=None, 
                 obj=None, state=None, method="POST", variable_decode=False, 
                 dict_char=".", list_char="-", multipart=False):

        self.request = request
        self.schema = schema
        self.validators = validators
        self.method = method
        self.variable_decode = variable_decode
        self.dict_char = dict_char
        self.list_char = list_char
        self.multipart = multipart
        self.state = state

        self.is_validated = False

        self.errors = {}
        self.data = {}

        if defaults:
            self.data.update(defaults)

        if obj:
            self.data.update(obj.__dict__)


        assert self.schema or self.validators, \
                "validators and/or schema required"

    def is_error(self, field):
        """
        Checks if individual field has errors.
        """
        return field in self.errors

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
                    self.errors[field] = unicode(e)

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

