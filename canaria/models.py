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

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

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
    id = Column(String(14), primary_key=True)
    name = Column(String(50))
    coal = Column(Boolean, default=False)
    mine_type = Column(String(20))
    status = Column(String(50))
    status_date = Column(Date)
    controller_start_date = Column(Date)
    district_id = Column(String(3))
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
    average_height = Column(Integer, default=0)
    methane_liberation = Column(Integer, default=0)

    @property
    def coal_or_metal(self):
        if self.coal:
            return 'C'
        return 'M'

    def set_coal_or_metal(self, c_or_m):
        self.coal = c_or_m == 'C'

class Controller(Base):
    __tablename__ = 'controller'
    id = Column(String(7), primary_key=True)
    name = Column(String(72))

# class Operator(Base):
#     pass

# class FieldOffice(Base):
#     pass

# class StandardIndustryClassification(Base):
#     pass

# class Canvass(Base):
#     pass

