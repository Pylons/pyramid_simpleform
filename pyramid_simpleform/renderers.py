import datetime
from webhelpers.html import tags
from webhelpers.html.builder import HTML


class Renderer(object):

    def __init__(self, data, errors, id_prefix=None):
        self.data = data
        self.errors = errors
        self.id_prefix = id_prefix

    def get_sequence(self, name, min_entries=0):

        data = self.value(name, [])
        errors = self.errors.get(name, {})

        return SequenceRenderer(name, data, errors, min_entries=min_entries)

    def get_mapping(self, name):

        data = self.value(name, {})
        errors = self.errors(name, [])

        return MappingRenderer(name, data, errors)

    def text(self, name, value=None, id=None, **attrs):
        """
        Outputs text input.
        """
        return tags.text(
            name, 
            self.value(name, value), 
            self._get_id(id, name), 
            **attrs
        )

    def date(self, name, value=None, id=None, date_format=None, **attrs):
        """
        Outputs text input with an optionally formatted datetime.
        """
        value = self.value(name, value)
        if isinstance(value, datetime.date) and date_format:
            value = value.strftime(date_format)

        return tags.text(
            name,
            value,
            self._get_id(id, name),
            **attrs
        )

    def file(self, name, value=None, id=None, **attrs):
        """
        Outputs file input.
        """
        return tags.file(
            name, 
            self.value(name, value), 
            self._get_id(id, name), 
            **attrs
        )

    def hidden(self, name, value=None, id=None, **attrs):
        """
        Outputs hidden input.
        """
        if value is None:
            value = self.value(name)

        return tags.hidden(
            name, 
            value, 
            self._get_id(id, name), 
            **attrs
        )

    def radio(self, name, value=None, checked=False, label=None, **attrs):
        """
        Outputs radio input.
        """
        checked = self.value(name) == value or checked
        return tags.radio(name, value, checked, label, **attrs)

    def submit(self, name, value=None, id=None, **attrs):
        """
        Outputs submit button.
        """
        return tags.submit(
            name, 
            self.value(name, value), 
            self._get_id(id, name), 
            **attrs
        )

    def select(self, name, options, selected_value=None, id=None, **attrs):
        """
        Outputs <select> element.
        """
        return tags.select(
            name, 
            self.value(name, selected_value), 
            options, 
            self._get_id(id, name), 
            **attrs
        )

    def checkbox(self, name, value="1", checked=False, label=None, id=None, 
                 **attrs):
        """
        Outputs checkbox input.
        """
    
        return tags.checkbox(
            name, 
            value, 
            self.value(name, checked), 
            label, 
            self._get_id(id, name), 
            **attrs
        )

    def textarea(self, name, content="", id=None, **attrs):
        """
        Outputs <textarea> element.
        """

        return tags.textarea(
            name, 
            self.value(name, content), 
            self._get_id(id, name), 
            **attrs
        )

    def password(self, name, value=None, id=None, **attrs):
        """
        Outputs a password input.
        """
        return tags.password(
            name, self.value(name, value), 
            self._get_id(id, name), 
            **attrs)

    def is_error(self, name):
        """
        Shortcut for **self.form.is_error(name)**
        """
        return name in self.errors

    def errors_for(self, name):
        """
        Shortcut for **self.form.errors_for(name)**
        """
        return self.form.errors_for(name)

    def all_errors(self):
        """
        Shortcut for **self.form.all_errors()**
        """
        return self.errors.values()

    def errorlist(self, name=None, **attrs):
        """
        Renders errors in a <ul> element. Unless specified in attrs, class
        will be "error".

        If no errors present returns an empty string.

        `name` : errors for name. If **None** all errors will be rendered.
        """

        if name is None:
            errors = self.all_errors()
        else:
            errors = self.errors_for(name)

        if not errors:
            return ''

        content = "\n".join(HTML.tag("li", error) for error in errors)
        
        if 'class_' not in attrs:
            attrs['class_'] = "error"

        return HTML.tag("ul", tags.literal(content), **attrs)

    def label(self, name, label=None, **attrs):
        """
        Outputs a <label> element. 

        `name`  : field name. Automatically added to "for" attribute.

        `label` : if **None**, uses the capitalized field name.
        """
        if 'for_' not in attrs:
            for_ = name.lower()
            if self.id_prefix:
                for_ = self.id_prefix + for_
            attrs['for_'] = for_
            
        label = label or name.capitalize()
        return HTML.tag("label", label, **attrs)

    def value(self, name, default=None):
        return self.data.get(name, default)

    def _get_id(self, id, name):
        if id is None:
            id = name
            if self.id_prefix:
                id = self.id_prefix + id
        return id


class FormRenderer(Renderer):
    """
    A simple form helper. Uses WebHelpers to render individual
    form widgets: see the WebHelpers library for more information
    on individual widgets.
    """

    def __init__(self, form, csrf_field='_csrf', id_prefix=None):

        self.form = form
        self.csrf_field = csrf_field

        super(FormRenderer, self).__init__(
            self.form.data, 
            self.form.errors, 
            id_prefix,
        )


    def begin(self, url=None, **attrs):
        """
        Creates the opening <form> tags.

        By default URL will be current path.
        """
        url = url or self.form.request.path
        multipart = attrs.pop('multipart', self.form.multipart)
        return tags.form(url, multipart=multipart, **attrs)

    def end(self):
        """
        Closes the form, i.e. outputs </form>.
        """
        return tags.end_form()
    
    def csrf(self, name=None):
        """
        Returns the CSRF hidden input. Creates new CSRF token
        if none has been assigned yet.

        The name of the hidden field is **_csrf** by default.
        """
        name = name or self.csrf_field

        token = self.form.request.session.get_csrf_token()
        if token is None:
            token = self.form.request.session.new_csrf_token()

        return self.hidden(name, value=token)

    def csrf_token(self, name=None):
        """
        Convenience function. Returns CSRF hidden tag inside hidden DIV.
        """
        return HTML.tag("div", self.csrf(name), style="display:none;")

    def hidden_tag(self, *names):
        """
        Convenience for printing all hidden fields in a form inside a 
        hidden DIV. Will also render the CSRF hidden field.

        :versionadded: 0.4
        """
        inputs = [self.hidden(name) for name in names]
        inputs.append(self.csrf())
        return HTML.tag("div", 
                        tags.literal("".join(inputs)), 
                        style="display:none;")


class SequenceRenderer(Renderer):

    def __init__(self, name, data, errors, id_prefix=None, min_entries=0):

        self.name = name
        
        num_entries = min_entries - len(data)
        if num_entries > 0:
            for i in xrange(num_entries):
                data.append({})

        super(SequenceRenderer, self).__init__(
            data,
            errors,
            id_prefix,
        )

    def begin(self):
        return self.hidden('__start__', value='%s:sequence' % self.name, id='')

    def end(self):
        return self.hidden('__end__', value='%s:sequence' % self.name, id='')

    def __iter__(self):
        
        # what kind of data we dealing with ?
    
        for i, d in enumerate(self.data):

            if not isinstance(d, dict):
                d = {self.name : d}

            errors = [] # to be determined
            id_prefix = "%d-" % i

            yield MappingRenderer(self.name, d, errors, id_prefix=id_prefix) 


class MappingRenderer(Renderer):

    def __init__(self, name, data, errors, id_prefix=None):

        self.name = name

        super(MappingRenderer, self).__init__(
            data,
            errors,
            id_prefix,
        )

    def begin(self, name=None):

        name = name or self.name

        return self.hidden('__start__', value='%s:mapping' % name, id='')

    def end(self, name=None):

        name = name or self.name

        return self.hidden('__end__', value='%s:mapping' % name, id='')


