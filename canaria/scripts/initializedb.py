import os
import sys
import transaction

from canaria.scripts import usage, bootstrap_script
from sqlalchemy import engine_from_config

from ..models import (
    DBSession,
    MyModel,
    Base,
    )

def main(argv=sys.argv):
    settings = bootstrap_script(argv)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)
