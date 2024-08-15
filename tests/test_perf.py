import time
from tests.test_data import building_limits, height_plateaus_complete
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    # Initial project deletion, if already exists
    client.delete("/delete-project",
                  params={"project_id": 2})

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


def test_concurrent_updates():
    def send_update_request(project_id, building_limits):
        response = client.put("/update-project",
                              params={"project_id": project_id},
                              json=building_limits)
        return response

    # Initial project deletion, if already exists
    client.delete("/delete-project",
                params={"project_id": 2})

    # Initial project creation
    create_response = client.post("/create-project",
                params={"project_id": 2},
                json={
        "building_limits": building_limits,
        "height_plateaus": height_plateaus_complete
    })
    assert create_response.status_code == 200

    # Prepare modified data for concurrent updates
    get_response = client.get(f"/building-limits/{2}")

    # Use ThreadPoolExecutor to simulate concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(send_update_request, 2, get_response.json()),
            executor.submit(send_update_request, 2, get_response.json()),
            executor.submit(send_update_request, 2, get_response.json()),
            executor.submit(send_update_request, 2, get_response.json()),
            executor.submit(send_update_request, 2, get_response.json())
        ]

        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    assert any(r.status_code == 200 for r in results)  # At least one should succeed
    assert any(r.status_code == 400 for r in results)  # At least one should detect a conflict
