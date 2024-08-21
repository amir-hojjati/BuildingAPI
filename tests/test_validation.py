import pytest
from fastapi.testclient import TestClient
from app.main import app
from .test_data import building_limits, height_plateaus_incomplete, \
    overlapping_plateaus

client = TestClient(app)


def test_height_plateaus_cover_building_limits():
    # Initial project deletion, if already exists
    client.delete("/delete-project",
                params={"project_id": 2})

    response = client.post("/create-project",
                           params={"project_id": 2},
                           json={
                               "building_limits": building_limits,
                               "height_plateaus": height_plateaus_incomplete
                           })
    assert response.status_code == 422
    assert ("Height plateaus do not completely cover the building limits"
            in response.json()["detail"])


def test_overlapping_height_plateaus():
    # Initial project deletion, if already exists
    client.delete("/delete-project",
                params={"project_id": 2})

    response = client.post("/create-project",
                           params={"project_id": 2},
                           json={
                               "building_limits": building_limits,
                               "height_plateaus": overlapping_plateaus
                           })
    assert response.status_code == 422
    assert "Height plateaus overlap" in response.json()["detail"]


def test_valid_geojson():
    # Initial project deletion, if already exists
    client.delete("/delete-project",
                  params={"project_id": 2})

    response = client.post("/create-project",
                           params={"project_id": 2},
                           json={
        "building_limits": {},
        "height_plateaus": {}  # Incomplete coverage
    })
    assert response.status_code == 422
    assert "Invalid GeoJSON" in response.json()["detail"]
