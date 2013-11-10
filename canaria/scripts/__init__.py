# package
import os, sys

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from sqlalchemy import engine_from_config

from ..models import (
    DBSession
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def bootstrap_script(argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    return settings

def bootstrap_sqlalchemy(settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    return engine

def bootstrap_script_and_sqlalchemy(argv):
    settings = bootstrap_script(argv)
    engine = bootstrap_sqlalchemy(settings)
    DBSession.configure(bind=engine)
    return settings, engine
