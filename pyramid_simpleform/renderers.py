import webhelpers.html.tags as h

from webhelpers.html.builder import HTML

class FormRenderer(object):
    """
    A simple form helper. Uses webhelpers to render individual
    form widgets.
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
        Returns the CSRF hidden input. Creates new CSRF token
        if none has been assigned yet.
        """
        token = self.request.session.get_csrf_token()
        if token is None:
            token = self.request.session.new_csrf_token()

        return self.hidden("_csrf", value=token)

    def csrf_token(self):
        """
        Convenience function. Returns CSRF hidden tag inside hidden DIV.
        """
        return HTML.tag("div", self.csrf(), style="display:none;")

    def text(self, name, value=None, id=None, **attrs):
        return tags.text(name, self.value(name, value), id, **attrs)

    def file(self, name, value=None, id=None, **attrs):
        return tags.file(name, self.value(name, value), id, **attrs)

    def hidden(self, name, value=None, id=None, **attrs):
        return tags.hidden(name, self.value(name, value), id, **attrs)

    def radio(self, name, value=None, checked=False, label=None, **attrs):
        checked = self.data.get(name) == value or checked
        return tags.radio(name, self.value(name, value), checked, label, **attrs)

    def submit(self, name, value=None, id=None, **attrs):
        return tags.submit(name, self.value(name, value), id, **attrs)

    def select(self, name, options, selected_value=None, id=None, **attrs):
        return tags.select(name, self.value(name, selected_value), 
                           options, id, **attrs)

    def checkbox(self, name, value="1", checked=False, label=None, id=None, 
                 **attrs):
    
        return tags.checkbox(name, value, self.value(name), label, id, **attrs)

    def textarea(self, name, content="", id=None, **attrs):
        return tags.textarea(name, self.value(name, content), id, **attrs)

    def password(self, name, value=None, id=None, **attrs):
        return tags.password(name, self.value(name, value), id, **attrs)

    def label(self, name, label=None, **attrs):
        if 'for_' not in attrs:
            attrs['for_'] = name
        label = label or name.capitalize()
        return HTML.tag("label", label, **attrs)
        


