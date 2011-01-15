from webhelpers.html import tags
from webhelpers.html.builder import HTML

class FormRenderer(object):
    """
    A simple form helper. Uses WebHelpers to render individual
    form widgets: see the WebHelpers library for more information
    on individual widgets.
    """

    def __init__(self, form):

        self.form = form
        self.request = self.form.request
        self.data = self.form.data
        self.errors = self.form.errors
        self.multipart = self.form.multipart

    def value(self, name, default=None):
        return self.data.get(name, default)

    def begin(self, url, **attrs):
        """
        Creates the opening <form> tags.
        """
        return tags.form(url, multipart=self.multipart, **attrs)

    def end(self):
        """
        Closes the form, i.e. outputs </form>.
        """
        return tags.end_form()
    
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
        """
        Outputs text input.
        """
        return tags.text(name, self.value(name, value), id, **attrs)

    def file(self, name, value=None, id=None, **attrs):
        """
        Outputs file input.
        """
        return tags.file(name, self.value(name, value), id, **attrs)

    def hidden(self, name, value=None, id=None, **attrs):
        """
        Outputs hidden input.
        """
        return tags.hidden(name, self.value(name, value), id, **attrs)

    def radio(self, name, value=None, checked=False, label=None, **attrs):
        """
        Outputs radio input.
        """
        checked = self.data.get(name) == value or checked
        return tags.radio(name, value, checked, label, **attrs)

    def submit(self, name, value=None, id=None, **attrs):
        """
        Outputs submit button.
        """
        return tags.submit(name, self.value(name, value), id, **attrs)

    def select(self, name, options, selected_value=None, id=None, **attrs):
        """
        Outputs <select> element.
        """
        return tags.select(name, self.value(name, selected_value), 
                           options, id, **attrs)

    def checkbox(self, name, value="1", checked=False, label=None, id=None, 
                 **attrs):
        """
        Outputs checkbox input.
        """
    
        return tags.checkbox(name, value, self.value(name), label, id, **attrs)

    def textarea(self, name, content="", id=None, **attrs):
        """
        Outputs <textarea> element.
        """
        return tags.textarea(name, self.value(name, content), id, **attrs)

    def password(self, name, value=None, id=None, **attrs):
        """
        Outputs a password input.
        """
        return tags.password(name, self.value(name, value), id, **attrs)

    def label(self, name, label=None, **attrs):
        """
        Outputs a <label> element. 

        `name`  : field name. Automatically added to "for" attribute.

        `label` : if **None**, uses the capitalized field name.
        """
        if 'for_' not in attrs:
            attrs['for_'] = name
        label = label or name.capitalize()
        return HTML.tag("label", label, **attrs)
        


