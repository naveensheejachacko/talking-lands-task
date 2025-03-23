# main.py
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from geoalchemy2 import Geometry
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from shapely.geometry import shape
from dotenv import load_dotenv
from app.models.spatial import PointData, PolygonData
from app.database import SessionLocal, engine, Base, get_db
from app.schemas.spatial import PointFeature, PointFeatureCollection, PolygonFeature,PolygonFeatureCollection
# Create tables
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Spatial Data Platform API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes for Point data
@app.post("/api/points", response_model=Dict)
def create_points(data: PointFeatureCollection, db: Session = Depends(get_db)):
    """
    Store multiple point data in GeoJSON format
    """
    if data.type != "FeatureCollection":
        raise HTTPException(status_code=400, detail="Invalid GeoJSON format. Must be a FeatureCollection.")
    
    created_points = []
    for feature in data.features:
        if feature.type != "Feature" or feature.geometry["type"] != "Point":
            raise HTTPException(status_code=400, detail="Invalid feature format. Must be Point type.")
        
        # Extract properties
        name = feature.properties.get("name", "Unnamed Point")
        description = feature.properties.get("description", "")
        
        # Extract coordinates
        coords = feature.geometry["coordinates"]
        wkt_point = f"POINT({coords[0]} {coords[1]})"
        
        # Create new point record
        db_point = PointData(
            name=name,
            description=description,
            geom=func.ST_GeomFromText(wkt_point, 4326)
        )
        
        db.add(db_point)
        db.flush()
        created_points.append(db_point.id)
    
    db.commit()
    return {"status": "success", "created_ids": created_points}

@app.get("/api/points", response_model=PointFeatureCollection)
def get_points(db: Session = Depends(get_db)):
    """
    Retrieve all point data as GeoJSON
    """
    points = db.query(PointData).all()
    
    features = []
    for point in points:
        # Convert geometry to GeoJSON
        geom_json = db.scalar(func.ST_AsGeoJSON(point.geom))
        geometry = json.loads(geom_json)
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": point.id,
                "name": point.name,
                "description": point.description,
                "created_at": point.created_at.isoformat(),
                "updated_at": point.updated_at.isoformat()
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/points/{point_id}", response_model=PointFeature)
def get_point(point_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific point by ID
    """
    point = db.query(PointData).filter(PointData.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    
    # Convert geometry to GeoJSON
    geom_json = db.scalar(func.ST_AsGeoJSON(point.geom))
    geometry = json.loads(geom_json)
    
    # Create feature
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "id": point.id,
            "name": point.name,
            "description": point.description,
            "created_at": point.created_at.isoformat(),
            "updated_at": point.updated_at.isoformat()
        }
    }
    
    return feature

@app.put("/api/points/{point_id}", response_model=Dict)
def update_point(point_id: int, feature: PointFeature, db: Session = Depends(get_db)):
    """
    Update an existing point
    """
    point = db.query(PointData).filter(PointData.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    
    if feature.type != "Feature" or feature.geometry["type"] != "Point":
        raise HTTPException(status_code=400, detail="Invalid feature format. Must be Point type.")
    
    # Update properties
    if "name" in feature.properties:
        point.name = feature.properties["name"]
    if "description" in feature.properties:
        point.description = feature.properties["description"]
    
    # Update geometry
    coords = feature.geometry["coordinates"]
    wkt_point = f"POINT({coords[0]} {coords[1]})"
    point.geom = func.ST_GeomFromText(wkt_point, 4326)
    point.updated_at = datetime.utcnow()
    
    db.commit()
    return {"status": "success", "updated_id": point_id}

@app.delete("/api/points/{point_id}", response_model=Dict)
def delete_point(point_id: int, db: Session = Depends(get_db)):
    """
    Delete a point by ID
    """
    point = db.query(PointData).filter(PointData.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    
    db.delete(point)
    db.commit()
    
    return {"status": "success", "deleted_id": point_id}

# Routes for Polygon data
@app.post("/api/polygons", response_model=Dict)
def create_polygons(data: PolygonFeatureCollection, db: Session = Depends(get_db)):
    """
    Store multiple polygon data in GeoJSON format
    """
    if data.type != "FeatureCollection":
        raise HTTPException(status_code=400, detail="Invalid GeoJSON format. Must be a FeatureCollection.")
    
    created_polygons = []
    for feature in data.features:
        if feature.type != "Feature" or feature.geometry["type"] != "Polygon":
            raise HTTPException(status_code=400, detail="Invalid feature format. Must be Polygon type.")
        
        # Extract properties
        name = feature.properties.get("name", "Unnamed Polygon")
        description = feature.properties.get("description", "")
        
        # Create WKT representation of the polygon
        polygon_shape = shape(feature.geometry)
        wkt_polygon = polygon_shape.wkt
        
        # Create new polygon record
        db_polygon = PolygonData(
            name=name,
            description=description,
            geom=func.ST_GeomFromText(wkt_polygon, 4326)
        )
        
        db.add(db_polygon)
        db.flush()
        created_polygons.append(db_polygon.id)
    
    db.commit()
    return {"status": "success", "created_ids": created_polygons}

@app.get("/api/polygons", response_model=PolygonFeatureCollection)
def get_polygons(db: Session = Depends(get_db)):
    """
    Retrieve all polygon data as GeoJSON
    """
    polygons = db.query(PolygonData).all()
    
    features = []
    for polygon in polygons:
        # Convert geometry to GeoJSON
        geom_json = db.scalar(func.ST_AsGeoJSON(polygon.geom))
        geometry = json.loads(geom_json)
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": polygon.id,
                "name": polygon.name,
                "description": polygon.description,
                "created_at": polygon.created_at.isoformat(),
                "updated_at": polygon.updated_at.isoformat()
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/polygons/{polygon_id}", response_model=PolygonFeature)
def get_polygon(polygon_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific polygon by ID
    """
    polygon = db.query(PolygonData).filter(PolygonData.id == polygon_id).first()
    if not polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")
    
    # Convert geometry to GeoJSON
    geom_json = db.scalar(func.ST_AsGeoJSON(polygon.geom))
    geometry = json.loads(geom_json)
    
    # Create feature
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "id": polygon.id,
            "name": polygon.name,
            "description": polygon.description,
            "created_at": polygon.created_at.isoformat(),
            "updated_at": polygon.updated_at.isoformat()
        }
    }
    
    return feature

@app.put("/api/polygons/{polygon_id}", response_model=Dict)
def update_polygon(polygon_id: int, feature: PolygonFeature, db: Session = Depends(get_db)):
    """
    Update an existing polygon
    """
    polygon = db.query(PolygonData).filter(PolygonData.id == polygon_id).first()
    if not polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")
    
    if feature.type != "Feature" or feature.geometry["type"] != "Polygon":
        raise HTTPException(status_code=400, detail="Invalid feature format. Must be Polygon type.")
    
    # Update properties
    if "name" in feature.properties:
        polygon.name = feature.properties["name"]
    if "description" in feature.properties:
        polygon.description = feature.properties["description"]
    
    # Update geometry
    polygon_shape = shape(feature.geometry)
    wkt_polygon = polygon_shape.wkt
    polygon.geom = func.ST_GeomFromText(wkt_polygon, 4326)
    polygon.updated_at = datetime.utcnow()
    
    db.commit()
    return {"status": "success", "updated_id": polygon_id}

@app.delete("/api/polygons/{polygon_id}", response_model=Dict)
def delete_polygon(polygon_id: int, db: Session = Depends(get_db)):
    """
    Delete a polygon by ID
    """
    polygon = db.query(PolygonData).filter(PolygonData.id == polygon_id).first()
    if not polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")
    
    db.delete(polygon)
    db.commit()
    
    return {"status": "success", "deleted_id": polygon_id}

# Spatial Queries
@app.get("/api/spatial/points-within-distance", response_model=PointFeatureCollection)
def points_within_distance(lat: float, lon: float, distance: float, db: Session = Depends(get_db)):
    """
    Find all points within a specific distance (in meters) from a given point
    """
    # Use text() for raw SQL to ensure proper PostGIS syntax
    query = db.query(PointData).filter(
        text("""
            ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :distance
            )
        """)
    ).params(lon=lon, lat=lat, distance=distance)
    
    points = query.all()
    
    features = []
    for point in points:
        geom_json = db.scalar(func.ST_AsGeoJSON(point.geom))
        geometry = json.loads(geom_json)
        
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": point.id,
                "name": point.name,
                "description": point.description,
                "created_at": point.created_at.isoformat(),
                "updated_at": point.updated_at.isoformat()
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/spatial/points-in-polygon/{polygon_id}", response_model=PointFeatureCollection)
def points_in_polygon(polygon_id: int, db: Session = Depends(get_db)):
    """
    Find all points that fall within a specific polygon
    """
    polygon = db.query(PolygonData).filter(PolygonData.id == polygon_id).first()
    if not polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")
    
    # Query points that are within the polygon
    query = db.query(PointData).filter(
        func.ST_Within(
            PointData.geom,
            polygon.geom
        )
    )
    
    points = query.all()
    
    features = []
    for point in points:
        # Convert geometry to GeoJSON
        geom_json = db.scalar(func.ST_AsGeoJSON(point.geom))
        geometry = json.loads(geom_json)
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": point.id,
                "name": point.name,
                "description": point.description,
                "created_at": point.created_at.isoformat(),
                "updated_at": point.updated_at.isoformat()
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/spatial/polygons-containing-point", response_model=PolygonFeatureCollection)
def polygons_containing_point(lat: float, lon: float, db: Session = Depends(get_db)):
    """
    Find all polygons that contain a specific point
    """
    # Use ST_DWithin with a small buffer to handle precision issues
    query = db.query(PolygonData).filter(
        text("""
            ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                1.0  -- 1 meter buffer
            )
        """)
    ).params(lon=lon, lat=lat)
    
    polygons = query.all()
    
    features = []
    for polygon in polygons:
        geom_json = db.scalar(func.ST_AsGeoJSON(polygon.geom))
        geometry = json.loads(geom_json)
        
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": polygon.id,
                "name": polygon.name,
                "description": polygon.description,
                "created_at": polygon.created_at.isoformat(),
                "updated_at": polygon.updated_at.isoformat()
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/spatial/overlapping-polygons/{polygon_id}", response_model=PolygonFeatureCollection)
def overlapping_polygons(polygon_id: int, db: Session = Depends(get_db)):
    """
    Find all polygons that overlap with a specific polygon
    """
    polygon = db.query(PolygonData).filter(PolygonData.id == polygon_id).first()
    if not polygon:
        raise HTTPException(status_code=404, detail="Polygon not found")
    
    # Query polygons that overlap with the specified polygon
    query = db.query(PolygonData).filter(
        PolygonData.id != polygon_id,  # Exclude the source polygon
        text("""
            ST_Intersects(
                geom,
                ST_SetSRID(ST_GeomFromText(:wkt), 4326)
            )
        """)
    ).params(wkt=db.scalar(func.ST_AsText(polygon.geom)))

    polygons = query.all()
    
    features = []
    for polygon in polygons:
        # Convert geometry to GeoJSON
        geom_json = db.scalar(func.ST_AsGeoJSON(polygon.geom))
        geometry = json.loads(geom_json)
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": polygon.id,
                "name": polygon.name,
                "description": polygon.description,
                "created_at": polygon.created_at.isoformat(),
                "updated_at": polygon.updated_at.isoformat()
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)