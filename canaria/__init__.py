from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('/', '/')
    # Also accept the following parameters:
    #  group=[state|county]
    #  
    config.add_route('apidocs', '/api')
    config.add_route('coalproduction_by_us', '/api/v1/coalproduction/{year}/us/*location')
    config.add_route('coalproduction_by_mine', '/api/v1/coalproduction/{year}/mine/{mine_id}')
    config.add_route('coalproduction_by_geo', '/api/v1/coalproduction/{year}/geo/{longitude},{latitude}')
    config.add_route('demo_map', '/demos/map')

    config.scan()
    return config.make_wsgi_app()
