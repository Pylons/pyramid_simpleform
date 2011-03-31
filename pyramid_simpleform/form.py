import colander
import peppercorn


class Form(object):


    """
    `request` : Pyramid request instance

    `schema`  : FormEncode Schema class or instance

    `defaults`   : a dict of default values

    `obj`        : instance of an object (e.g. SQLAlchemy model)

    `method`        : HTTP method

    Also note that values of ``obj`` supercede those of ``defaults``. Only
    fields specified in your schema or validators will be taken from the 
    object.
    """


    def __init__(self, request, schema=None, defaults=None, 
                 obj=None, extra=None, include=None, exclude=None,
                 method="POST", multipart=False):

        self.request = request
        self.schema = schema
        self.method = method
        self.multipart = multipart

        self.is_validated = False

        self.errors = {}
        self.data = {}

        self.non_field_errors = []

        if defaults:
            self.data.update(defaults)

        if obj:
            fields = [node.name for node in self.schema]
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
        errors = self.non_field_errors[:]
        for node in self.schema:
            errors += self.errors_for(node.name)
        return errors

    def errors_for(self, field):
        """
        Returns any errors for a given field as a list.
        """
        errors = self.errors.get(field, [])
        if isinstance(errors, basestring):
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
        will use **request.POST** (if HTTP POST) or **request.params**.
        """

        if self.is_validated:
            return not(self.errors)

        if not force_validate:
            if self.method and self.method != self.request.method:
                return False

        if params is None:
            if self.method == "POST":
                params = self.request.POST
            else:
                params = self.request.params
            
        params = peppercorn.parse(params.items())
        self.data.update(params)

        if self.schema:
            try:
                self.data = self.schema.deserialize(params)
            except colander.Invalid, e:
                self.errors = e.asdict()

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
            raise RuntimeError, \
                    "Form has not been validated. Call validate() first"

        if self.errors:
            raise RuntimeError, "Cannot bind to object if form has errors"

        items = [(k, v) for k, v in self.data.items() if not k.startswith("_")]
        for k, v in items:

            if include and k not in include:
                continue

            if exclude and k in exclude:
                continue

            setattr(obj, k, v)

        return obj


