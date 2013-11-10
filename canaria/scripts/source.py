import sys
from canaria.scripts import usage, bootstrap_script_and_sqlalchemy

def download_sources(argv=sys.argv):
    print("download_sources")
    settings, engine = bootstrap_script_and_sqlalchemy(argv)

def import_sources(argv=sys.argv):
    print("import_sources")
    settings, engine = bootstrap_script_and_sqlalchemy(argv)

