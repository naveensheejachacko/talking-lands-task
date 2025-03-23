from pydantic import BaseModel
from datetime import datetime
from typing import Optional
# Pydantic models for request and response
class PointFeature(BaseModel):
    type: str
    geometry: dict
    properties: dict

class PointFeatureCollection(BaseModel):
    type: str
    features: list[PointFeature]

class PolygonFeature(BaseModel):
    type: str
    geometry: dict
    properties: dict

class PolygonFeatureCollection(BaseModel):
    type: str
    features: list[PolygonFeature]

class DataResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    geom: str
