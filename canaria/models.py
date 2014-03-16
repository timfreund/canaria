from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from geoalchemy2 import Geometry

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

class Mine(Base):
    __tablename__ = 'mine'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    coal = Column(Boolean, default=False)
    mine_type = Column(String(20))
    status = Column(String(50))
    status_date = Column(Date)
    controller_id = Column(String(7), ForeignKey('controller.id'), nullable=True)
    controller_start_date = Column(Date)
    operator_id = Column(String(7), ForeignKey('operator.id'), nullable=True)
    district_id = Column(String(3))
    field_office_id = Column(String(5), ForeignKey('field_office.id'), nullable=True)
    provided_state = Column(String(64))
    provided_county = Column(String(64))
    fips_county_code = Column(Integer)
    assess_control_number = Column(String(20))
    current_103i_status = Column(String(80))
    current_103i_date = Column(Date)
    portable = Column(Boolean)
    portable_fips_state_code = Column(String(2))
    days_per_week = Column(Integer, default=0)
    hours_per_shift = Column(Integer, default=0)
    production_shifts = Column(Integer, default=0)
    maintenance_shifts = Column(Integer, default=0)
    employees = Column(Integer, default=0)
    part48 = Column(Boolean, default=False)
    longitude = Column(Float)
    latitude = Column(Float)
    location = Column(Geometry('POINT', srid=4326, management=True))
    average_height = Column(Integer, default=0)
    methane_liberation = Column(Integer, default=0)

    @property
    def coal_or_metal(self):
        if self.coal:
            return 'C'
        return 'M'

    def set_coal_or_metal(self, c_or_m):
        self.coal = c_or_m == 'C'

class Activity(Base):
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    mine_id = Column(Integer, ForeignKey('mine.id'), nullable=True)
    mine_name = Column(String(50))
    provided_state = Column(String(64))
    provided_county = Column(String(64))
    basin = Column(String(64))
    status = Column(String(64))
    mine_type = Column(String(64))
    company_type = Column(String(64))
    operation = Column(String(64))
    operating_company = Column(String(64))
    company_address = Column(String(64))
    union = Column(String(64))
    production = Column(Integer)
    average_employees = Column(Integer)
    labor_hours = Column(Integer)

    def __json__(self, request):
        json = {}
        for c in Activity.__table__.columns:
            json[c.name] = getattr(self, c.name)
        return json

class Controller(Base):
    __tablename__ = 'controller'
    id = Column(String(7), primary_key=True)
    name = Column(String(72))

class County(Base):
    __tablename__ = 'county'
    id = Column(Integer, primary_key=True)
    ansi_state = Column(Integer, nullable=False)
    ansi_county = Column(Integer, nullable=False)
    postal_state = Column(String(2), nullable=False)
    state_name = Column(Text, nullable=True)
    county_name = Column(Text, nullable=False)

class FieldOffice(Base):
    __tablename__ = 'field_office'
    id = Column(String(5), primary_key=True)
    name = Column(String(64))

class Operator(Base):
    __tablename__ = 'operator'
    id = Column(String(7), primary_key=True)
    name = Column(String(64))
    company_type = Column(String(64))

# class StandardIndustryClassification(Base):
#     pass

# class Canvass(Base):
#     pass

