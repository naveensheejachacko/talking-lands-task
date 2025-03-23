# Spatial Data Platform API Documentation

A FastAPI-based service for managing spatial data with points and polygons using PostGIS.

## Setup and Installation

1. Prerequisites:
   - PostgreSQL with PostGIS extension
   - Python 3.8+
   - Virtual environment (recommended)

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database in `.env`

## API Documentation

### 1. Points API

#### Create Points
```http
POST /api/points
Content-Type: application/json

# Request Body:
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [77.5946, 12.9716]
      },
      "properties": {
        "name": "Tech Park",
        "description": "Software Technology Park"
      }
    }
  ]
}

# Response:
{
  "status": "success",
  "created_ids": [1]
}
```

### 2. Polygons API

#### Create Polygon
```http
POST /api/polygons
Content-Type: application/json

# Request Body:
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [77.5945, 12.9715],
          [77.5948, 12.9715],
          [77.5948, 12.9718],
          [77.5945, 12.9718],
          [77.5945, 12.9715]
        ]]
      },
      "properties": {
        "name": "Campus Area",
        "description": "University Campus"
      }
    }
  ]
}
```

### 3. Spatial Queries

#### Points Within Distance
```http
GET /api/spatial/points-within-distance?lat=12.9716&lon=77.5946&distance=1000

# Response:
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [77.5946, 12.9716]
      },
      "properties": {
        "id": 1,
        "name": "Tech Park",
        "description": "Software Technology Park",
        "created_at": "2023-12-20T10:30:00",
        "updated_at": "2023-12-20T10:30:00"
      }
    }
  ]
}
```

## Example Data Files

The `/examples` directory contains sample data for testing:

1. `demo-points.json` - Sample point data
2. `demo-polygon.json` - Sample polygon data
3. `test_spatial.py` - Python script for testing endpoints

## Testing

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Run the test script:
```bash
python examples/test_spatial.py
```

## API Reference

### Points API
- POST /api/points - Create points
- GET /api/points - List all points
- GET /api/points/{id} - Get point by ID
- PUT /api/points/{id} - Update point
- DELETE /api/points/{id} - Delete point

### Polygons API
- POST /api/polygons - Create polygons
- GET /api/polygons - List all polygons
- GET /api/polygons/{id} - Get polygon by ID
- PUT /api/polygons/{id} - Update polygon
- DELETE /api/polygons/{id} - Delete polygon

### Spatial Queries
- GET /api/spatial/points-within-distance - Find points within distance
- GET /api/spatial/points-in-polygon/{polygon_id} - Find points in polygon
- GET /api/spatial/polygons-containing-point - Find polygons containing point
- GET /api/spatial/overlapping-polygons/{polygon_id} - Find overlapping polygons

## Notes
- All coordinates are in [longitude, latitude] format
- Distances are in meters
- Using WGS84 (EPSG:4326) coordinate system


![image](https://github.com/user-attachments/assets/a44a6f4d-d29c-4712-b5b9-34ab471e163f)
