import logging

from pyramid.view import action
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPFound
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from formencode import Schema, validators

from simplesite.models import MyModel, Session

class MyModelSchema(Schema):

    filter_extra_fields = True
    allow_extra_fields = True

    name = validators.MinLength(5, not_empty=True)
    value = validators.Int(not_empty=True)


log = logging.getLogger(__name__)

class MainHandler(object):
    def __init__(self, request):
        self.request = request

    @action(renderer='index.html')
    def index(self):
        items = Session().query(MyModel).all()
        return dict(items=items)

    @action(renderer='edit.html')
    def edit(self):

        session = Session()

        item_id = self.request.matchdict['item_id']
        item = session.query(MyModel).get(item_id)

        form = Form(self.request, schema=MyModelSchema, obj=item)

        if form.validate():
            
            form.bind(item)
            session.merge(item)
            session.flush()
            
            return HTTPFound(location="/")

        return dict(item=item, form=FormRenderer(form))

    @action(renderer='submit.html')
    def submit(self):
        
        form = Form(self.request, schema=MyModelSchema)

        if form.validate():

            obj = form.bind(MyModel())

            session = Session()
            session.add(obj)
            session.flush()

            return HTTPFound(location="/")

        return dict(form=FormRenderer(form))
