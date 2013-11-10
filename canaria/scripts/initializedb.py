import os
import sys
import transaction

from canaria.scripts import usage, bootstrap_script_and_sqlalchemy
from sqlalchemy import engine_from_config

from ..models import (
    DBSession,
    MyModel,
    Base,
    )

def main(argv=sys.argv):
    settings, engine = bootstrap_script_and_sqlalchemy(argv)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)
