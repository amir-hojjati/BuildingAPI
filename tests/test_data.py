# tests/test_data.py
building_limits = {
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
            "properties": {}
        }
    ]
}

height_plateaus_complete = {
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
                "elevation": 5.0
            }
        }
    ]
}

height_plateaus_incomplete = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [15.0, 15.0],
                        [25.0, 15.0],
                        [25.0, 25.0],
                        [15.0, 25.0],
                        [15.0, 15.0]
                    ]
                ]
            },
            "properties": {
                "elevation": 6.0
            }
        }
    ]
}

overlapping_plateaus = {
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
                "elevation": 5.0
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [15.0, 15.0],
                        [25.0, 15.0],
                        [25.0, 25.0],
                        [15.0, 25.0],
                        [15.0, 15.0]
                    ]
                ]
            },
            "properties": {
                "elevation": 6.0
            }
        }
    ]
}
