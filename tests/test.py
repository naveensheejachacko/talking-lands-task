import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_point_operations():
    # Create points
    with open('tests/demo-points.json') as f:
        points_data = json.load(f)
    
    # Test POST /api/points
    response = requests.post(f"{BASE_URL}/points", json=points_data)
    point_id = response.json()["created_ids"][0]
    print("Created points:", response.json())
    
    # Test GET /api/points
    response = requests.get(f"{BASE_URL}/points")
    print("\nList all points:", json.dumps(response.json(), indent=2))
    
    # Test GET /api/points/{id}
    response = requests.get(f"{BASE_URL}/points/{point_id}")
    print(f"\nGet point {point_id}:", json.dumps(response.json(), indent=2))
    
    # Test PUT /api/points/{id}
    update_data = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [77.5946, 12.9716]
        },
        "properties": {
            "name": "Updated Tech Park",
            "description": "Updated Description"
        }
    }
    response = requests.put(f"{BASE_URL}/points/{point_id}", json=update_data)
    print(f"\nUpdate point {point_id}:", response.json())
    
    # Test points within distance
    params = {
        "lat": 12.9716,
        "lon": 77.5946,
        "distance": 1000
    }
    response = requests.get(f"{BASE_URL}/spatial/points-within-distance", params=params)
    print("\nPoints within distance:", json.dumps(response.json(), indent=2))

def test_polygon_operations():
    # Create polygon
    with open('tests/demo-polygon.json') as f:
        polygon_data = json.load(f)
    
    # Test POST /api/polygons
    response = requests.post(f"{BASE_URL}/polygons", json=polygon_data)
    polygon_id = response.json()["created_ids"][0]
    print("Created polygon:", response.json())
    
    # Test GET /api/polygons
    response = requests.get(f"{BASE_URL}/polygons")
    print("\nList all polygons:", json.dumps(response.json(), indent=2))
    
    # Test GET /api/polygons/{id}
    response = requests.get(f"{BASE_URL}/polygons/{polygon_id}")
    print(f"\nGet polygon {polygon_id}:", json.dumps(response.json(), indent=2))
    
    # Test PUT /api/polygons/{id}
    update_data = {
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
            "name": "Updated Campus Area",
            "description": "Updated University Campus"
        }
    }
    response = requests.put(f"{BASE_URL}/polygons/{polygon_id}", json=update_data)
    print(f"\nUpdate polygon {polygon_id}:", response.json())

def test_spatial_queries():
    # Test points in polygon
    response = requests.get(f"{BASE_URL}/spatial/points-in-polygon/1")
    print("\nPoints in polygon:", json.dumps(response.json(), indent=2))
    
    # Test polygons containing point
    params = {
        "lat": 12.9716,
        "lon": 77.5946
    }
    response = requests.get(f"{BASE_URL}/spatial/polygons-containing-point", params=params)
    print("\nPolygons containing point:", json.dumps(response.json(), indent=2))
    
    # Test overlapping polygons
    response = requests.get(f"{BASE_URL}/spatial/overlapping-polygons/1")
    print("\nOverlapping polygons:", json.dumps(response.json(), indent=2))

def cleanup_tests():
    # Delete test points
    response = requests.get(f"{BASE_URL}/points")
    points = response.json()
    for point in points['features']:
        point_id = point['properties']['id']
        response = requests.delete(f"{BASE_URL}/points/{point_id}")
        print(f"\nDeleted point {point_id}:", response.json())
    
    # Delete test polygons
    response = requests.get(f"{BASE_URL}/polygons")
    polygons = response.json()
    for polygon in polygons['features']:
        polygon_id = polygon['properties']['id']
        response = requests.delete(f"{BASE_URL}/polygons/{polygon_id}")
        print(f"\nDeleted polygon {polygon_id}:", response.json())

if __name__ == "__main__":
    print("Testing Point Operations:")
    test_point_operations()
    
    print("\nTesting Polygon Operations:")
    test_polygon_operations()
    
    print("\nTesting Spatial Queries:")
    test_spatial_queries()
    
    print("\nCleaning up test data:")
    cleanup_tests()