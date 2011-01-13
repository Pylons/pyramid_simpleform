import pyramid_beaker
import pyramid_sqla

from pyramid.config import Configurator
from pyramid_sqla.static import add_static_route

from simplesite.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    # Initialize database
    engine = pyramid_sqla.add_engine(settings, prefix='sqlalchemy.')
    initialize_sql(engine)

    # Configure Beaker sessions
    session_factory = pyramid_beaker.session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    # Configure renderers
    config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')
    config.add_subscriber('simplesite.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')

    # Set up routes and views
    config.add_handler('home', '/', 'simplesite.handlers:MainHandler',
                       action='index')
    
    config.add_handler('add', '/submit/', 'simplesite.handlers:MainHandler',
                       action='submit')


    config.add_handler('main', '/{action}', 'simplesite.handlers:MainHandler',
        path_info=r'/(?!favicon\.ico|robots\.txt|w3c)')
    add_static_route(config, 'simplesite', 'static', cache_max_age=3600)

    return config.make_wsgi_app()
