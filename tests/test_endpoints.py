from fastapi.testclient import TestClient
from app.main import app
from .test_data import building_limits, height_plateaus_complete

client = TestClient(app)


def test_create_project():
    # Initial project deletion, if already exists
    client.delete("/delete-project",
                  params={"project_id": 2})

    # Good request
    response = client.post("/create-project",
                           params={"project_id": 2},
                           json={
        "building_limits": building_limits,
        "height_plateaus": height_plateaus_complete
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully split and stored the results"

    # Initial project deletion, if already exists
    client.delete("/delete-project",
                  params={"project_id": 2})

    # Bad request
    response = client.post("/create-project",
                           params={"project_id": 2},
                           json={
                               "building_limits": {},
                               "height_plateaus": {}
                           })
    assert response.status_code == 422


def test_update_project():
    updated_height_plateaus = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [10.0, 10.0],
                            [20.0, 10.0],
                            [20.0, 20.0],
                            [10.0, 20.0],
                            [10.0, 10.0]
                        ]
                    ]
                },
                "properties": {
                    "elevation": 10.0
                }
            }
        ]
    }

    response = client.put("/update-project",
                          params={"project_id": 2},
                          json={
        "building_limits": building_limits,
        "height_plateaus": updated_height_plateaus
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "404: Project with this ID does not exist."
