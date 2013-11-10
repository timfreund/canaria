import os, sys
import time
import urllib2
from canaria.scripts import usage, bootstrap_script_and_sqlalchemy


def download_sources(argv=sys.argv):
    settings, engine = bootstrap_script_and_sqlalchemy(argv)

    if not settings.has_key('canaria.sources'):
        print "canaria.sources is not defined in your configuration file."
        print "Please set it to a directory for local data source storage."
    
    annual_production_url = "http://www.eia.gov/coal/data/public/xls/coalpublic%d.xls"
    source_urls = [annual_production_url % year for year in range(1983, 2012)]
    source_urls.append("http://www.msha.gov/OpenGovernmentData/DataSets/Mines.zip")

    src_dir = settings['canaria.sources']
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    for url in source_urls:
        file_name = url.rsplit('/', 1)[1]
        file_path = os.path.sep.join([src_dir, file_name])
        if os.path.exists(file_path):
            print "%s already exists, skipping download" % file_path
        else:
            print "Downloading %s to %s" % (file_name, file_path)
            dest_file = open(file_path, "w")
            dest_file.write(urllib2.urlopen(url).read())
            dest_file.close()
            time.sleep(10)

def import_sources(argv=sys.argv):
    print("import_sources")
    settings, engine = bootstrap_script_and_sqlalchemy(argv)

