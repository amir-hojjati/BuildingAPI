import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_large_input_performance():
    large_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [i, j],
                            [i + 10, j],
                            [i + 10, j + 10],
                            [i, j + 10],
                            [i, j]
                        ]
                    ]
                },
                "properties": {'elevation': 1}
            }
            for i in range(0, 100, 10)
            for j in range(0, 100, 10)
        ]
    }

    start_time = time.time()
    response = client.post("/create-project",
                           params={"project_id": 2},
                           json={
        "building_limits": large_geojson,
        "height_plateaus": large_geojson
    })
    duration = time.time() - start_time

    assert response.status_code == 200
    # Ensure it completes within 5 seconds
    assert duration < 5
