from sqlalchemy import Column, Integer, String, DateTime
from geoalchemy2 import Geometry
from datetime import datetime
from ..database import Base

class PointData(Base):
    __tablename__ = "point_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    geom = Column(Geometry("POINT", srid=4326))

class PolygonData(Base):
    __tablename__ = "polygon_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    geom = Column(Geometry("POLYGON", srid=4326))
