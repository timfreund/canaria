import xml.etree.ElementTree as ET
import logging
import os, sys
import time
import transaction
import urllib2
from canaria.scripts import usage, bootstrap_script_and_sqlalchemy
from canaria.models import Controller, DBSession, Mine
from canaria import models
from datetime import datetime, date, timedelta

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    )

log = logging.getLogger('canaria.scripts')

class ObjectImportContainer(object):
    def __init__(self):
        self.objs = {}

    def __getitem__(self, key):
        if not self.objs.has_key(key):
            new_obj = getattr(models, key)()
            self.objs[key] = new_obj
        return self.objs[key]

    def __setitem(self, key, value):
        self.objs[key] = value

    def values(self):
        return self.objs.values()

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
    settings, engine = bootstrap_script_and_sqlalchemy(argv)
    import_mines(settings, engine)
    import_activities(settings, engine)

def import_activities(settings, engine):
    src_template = os.path.sep.join([settings['canaria.sources'], "coalpublic%d.xls"])
    src_files = [src_template % year for year in range(1983, 2012)]

    for src_file in src_files:
        tree = ET.parse(src_file)
        import_activities_file(settings, engine, tree)

def import_activities_file(settings, engine, tree):
    rows = tree.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Row')
    headers = []
    for datum in rows[3].findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Data'):
        headers.append(datum.text)
    for row in rows[4:]:
        values = [datum.text for datum in row.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Data')]
        activity = {}
        for k, v in zip(headers, values):
            activity[k] = v
        import_activities_record(settings, engine, activity)

def import_activities_record(settings, engine, activity):
    if activity['MSHA ID'] == None:
        log.error("No MSHA ID, skipping")
    else:
        import_object(activity, activity_column_map)

def import_mines(settings, engine):
    import csv, zipfile
    src_path = os.path.sep.join([settings['canaria.sources'], 'Mines.zip'])
    dest_path = os.path.sep.join([settings['canaria.sources'], 'Mines.txt'])
    with zipfile.ZipFile(src_path) as mines_zip:
        mines_zip_txt = mines_zip.open("Mines.txt", "r")
        with open(dest_path, "w") as mines_txt:
            mines_txt.write(mines_zip_txt.read())

    with open(dest_path, 'r') as mine_file:
        mines = csv.DictReader(mine_file, delimiter='|')
        for row in mines:
            import_object(row, mine_column_map)

def import_object(obj, attr_map):
    transaction.begin()
    objects = ObjectImportContainer()
    for k, v in obj.items():
        if attr_map.has_key(k):
            dests = attr_map[k]
            for dest in dests:
                obj_name, attr_name = dest.split('.')
                obj = objects[obj_name]
                if attr_name.find('()') > 0:
                    getattr(obj, attr_name.replace('()', ''))(v)
                    break
                if not hasattr(obj, attr_name):
                    print "Missing attribute: %s" % dest
                    break
                setattr(obj, attr_name, convert_data(getattr(obj.__class__, 
                                                             attr_name), v))
    for obj in objects.values():
        preexist = DBSession.query(obj.__class__).filter(obj.__class__.id == obj.id).first()
        if not preexist:
            if isinstance(obj, Controller) and obj.id == None:
                pass
            else:
                DBSession.add(obj)
    transaction.commit()

def convert_data(attr, value):
    if value == '' or value == '-':
        return None

    t = attr.property.columns[0].type
    if isinstance(t, Date):
        return datetime.strptime(value, '%m/%d/%Y').date()
    elif isinstance(t, Boolean):
        return value == 'Y'
    return value

activity_column_map = {
    'Year': ['Activity.year'],
    'MSHA ID': ['Activity.mine_id'],
    'Mine Name': ['Activity.mine_name'],
    'Mine State': ['Activity.state'],
    'Mine County': ['Activity.county'],
    'Mine Basin': ['Activity.basin'],
    'Mine Status': ['Activity.status'],
    'Mine Type': ['Activity.mine_type'],
    'Company Type': ['Activity.company_type'],
    'Operation Type': ['Activity.operation'],
    'Operating Company': ['Activity.operating_company'],
    'Operating Company Address': ['Activity.company_address'],
    'Union Code': ['Activity.union'],
    'Production (short tons)': ['Activity.production'],
    'Average Employees': ['Activity.average_employees'],
    'Labor Hours': ['Activity.labor_hours'],
}
        
mine_column_map = dict(
    MINE_ID = ['Mine.id'],
    CURRENT_MINE_NAME = ['Mine.name'],
    COAL_METAL_IND = ['Mine.set_coal_or_metal()'],
    CURRENT_MINE_TYPE = ['Mine.mine_type'],
    CURRENT_MINE_STATUS = ['Mine.status'],
    CURRENT_STATUS_DT = ['Mine.status_date'],
    CURRENT_CONTROLLER_ID = ['Controller.id', 'Mine.controller_id'],
    CURRENT_CONTROLLER_NAME = ['Controller.name'],
    # CURRENT_OPERATOR_ID = ['Operator.id', 'Mine.operator_id'],
    # CURRENT_OPERATOR_NAME = ['Operator.name'],
    # STATE = ['Operator.state'],
    # BOM_STATE_CD = ['Operator.bom_state_code'],
    # FIPS_CNTY_CD = ['Operator.fips_county_code'],
    # FIPS_CNTY_NM = ['Operator.fips_county_name'],
    # CONG_DIST_CD = ['Operator.cong_dist_code'],
    # COMPANY_TYPE = ['Operator.company_type'],
    CURRENT_CONTROLLER_BEGIN_DT = ['Mine.controller_start_date'],
    DISTRICT = ['Mine.district_id'],
    # OFFICE_CD = ['FieldOffice.id'],
    # OFFICE_NAME = ['FieldOffice.name'],
    ASSESS_CTRL_NO = ['Mine.assess_control_number'],
    # PRIMARY_SIC_CD = ['StandardIndustryClassification.id', 'Mine.primary_sic_id'],
    # PRIMARY_SIC = ['StandardIndustryClassification.name'],
    # PRIMARY_SIC_CD_1 = [],
    # PRIMARY_SIC_CD_SFX = [],
    # SECONDARY_SIC_CD = ['StandardIndustryClassification.id', 'Mine.secondary_sic_id'],
    # SECONDARY_SIC = ['StandardIndustryClassification.name'],
    # SECONDARY_SIC_CD_1 = [],
    # SECONDARY_SIC_CD_SFX = [],
    # PRIMARY_CANVASS_CD = ['Canvass.id', 'Mine.primary_canvass_id'],
    # PRIMARY_CANVASS = ['Canvass.name'],
    # SECONDARY_CANVASS_CD = ['Canvass.id', 'Mine.secondary_canvass_id'],
    # SECONDARY_CANVASS = ['Canvass.name'],
    CURRENT_103I = ['Mine.current_103i_status'],
    CURRENT_103I_DT = ['Mine.current_103i_date'],
    PORTABLE_OPERATION = ['Mine.portable'],
    PORTABLE_FIPS_ST_CD = ['Mine.portable_fips_state_code'],
    DAYS_PER_WEEK = ['Mine.days_per_week'],
    HOURS_PER_SHIFT = ['Mine.hours_per_shift'],
    PROD_SHIFTS_PER_DAY = ['Mine.production_shifts'],
    MAINT_SHIFTS_PER_DAY = ['Mine.maintenance_shifts'],
    NO_EMPLOYEES = ['Mine.employees'],
    PART48_TRAINING = ['Mine.part48'],
    LONGITUDE = ['Mine.latitude'],
    LATITUDE = ['Mine.longitude'],
    AVG_MINE_HEIGHT = ['Mine.average_height'],
    MINE_GAS_CATEGORY_CD = [],
    METHANE_LIBERATION = ['Mine.methane_liberation'],
    NO_PRODUCING_PITS = [],
    NO_NONPRODUCING_PITS = [],
    NO_TAILING_PONDS = [],
    PILLAR_RECOVERY_USED = [],
    HIGHWALL_MINER_USED = [],
    MULTIPLE_PITS = [],
    MINERS_REP_IND = [],
    SAFETY_COMMITTEE_IND = [],
    MILES_FROM_OFFICE = [],
    DIRECTIONS_TO_MINE = [],
    NEAREST_TOWN = [],
)
