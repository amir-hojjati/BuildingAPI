# app/tools.py
import geopandas as gpd
from shapely.geometry import shape, mapping
from shapely.geometry.base import BaseGeometry

from app.models import SplitBuildingLimit


def validate_coverage(building_limits_gdf, height_plateaus_gdf):
    """
    Validates that height plateaus completely cover building limits.

    :param building_limits_gdf: GeoDataFrame of building limits
    :param height_plateaus_gdf: GeoDataFrame of height plateaus
    :return: None if valid, raises ValueError if invalid
    """
    combined_plateaus = height_plateaus_gdf.unary_union
    for _, row in building_limits_gdf.iterrows():
        limit_geom = row.geometry
        # Check if plateaus cover building limits (allow minimal buffer)
        if not combined_plateaus.buffer(1e-6).contains(limit_geom):
            raise ValueError("Height plateaus do not completely cover the building limits.")


def split_limits(building_limits_geojson, height_plateaus_geojson):
    """
    Splits building limits according to height plateaus.

    :param building_limits_geojson: GeoJSON data for building limits
    :param height_plateaus_geojson: GeoJSON data for height plateaus
    :return: Tuple containing split limits, building limits, and height plateaus GeoDataFrames
    """
    building_limits_gdf = validate_geojson(building_limits_geojson)
    height_plateaus_gdf = validate_geojson(height_plateaus_geojson)

    # Ensure building limits and height plateaus have valid geometries
    if not building_limits_gdf.is_valid.all() or not height_plateaus_gdf.is_valid.all():
        raise ValueError("Invalid geometries in input data")

    # Validate that height plateaus completely cover the building limits
    validate_coverage(building_limits_gdf, height_plateaus_gdf)

    # Perform intersection to split building limits by height plateaus
    splits = gpd.overlay(building_limits_gdf, height_plateaus_gdf, how='intersection')

    return splits, building_limits_gdf, height_plateaus_gdf


def store_processed_splits(db, split_gdf, project_id, stored_limits, stored_plateaus):
    """
    Processes and stores split geometries and links them to the original building limits and height plateaus.

    :param db: Database session
    :param split_gdf: GeoDataFrame containing split geometries
    :param project_id: Project ID for which splits are processed
    :param stored_limits: List of stored BuildingLimit objects
    :param stored_plateaus: List of stored HeightPlateau objects
    :return: None
    """
    # Create a mapping from geometry to ID
    limit_geometry_to_id = {shape(limit.geometry): limit.id for limit in stored_limits}
    plateau_geometry_to_id = {shape(plateau.geometry): plateau.id for plateau in stored_plateaus}

    # Link splits to the original limits and plateaus
    for _, row in split_gdf.iterrows():
        split_geom = row.geometry
        matching_limit_id = None
        matching_plateau_id = None

        for limit_geom, limit_id in limit_geometry_to_id.items():
            if limit_geom.contains(split_geom):
                matching_limit_id = limit_id
                break
            elif limit_geom.buffer(1e-9).contains(split_geom):
                matching_limit_id = limit_id
                break

        for plateau_geom, plateau_id in plateau_geometry_to_id.items():
            if plateau_geom.contains(split_geom):
                matching_plateau_id = plateau_id
                break
            elif plateau_geom.buffer(1e-9).contains(split_geom):
                matching_plateau_id = plateau_id
                break

        if matching_limit_id is None or matching_plateau_id is None:
            raise ValueError("Failed to match split polygon to original building limit or height plateau")

        split_elevation = next(plateau.elevation for plateau in stored_plateaus if plateau.id == matching_plateau_id)
        new_split = SplitBuildingLimit(
            project_id=project_id,
            version=1,
            elevation=split_elevation,
            geometry=mapping(split_geom),
            building_limit_id=matching_limit_id,
            height_plateau_id=matching_plateau_id
        )
        db.add(new_split)

    db.commit()


def validate_geojson(geojson):
    """
    Validates that the provided GeoJSON has a valid structure and geometry.

    :param geojson: GeoJSON data to validate
    :return: GeoDataFrame with validated geometry
    """
    try:
        if "features" not in geojson:
            raise ValueError("Invalid GeoJSON format.")
        gdf = gpd.GeoDataFrame.from_features(geojson["features"])
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise ValueError("Invalid GeoJSON format.")

        # Ensure there's a valid geometry column
        if 'geometry' not in gdf.columns:
            raise ValueError("GeoJSON does not contain a 'geometry' column.")

        # Set the active geometry column
        gdf = gdf.set_geometry('geometry')

        # Ensure all geometries are valid and of correct type (Polygon)
        for geom in gdf.geometry:
            if not isinstance(geom, BaseGeometry):
                raise ValueError("Invalid geometry in GeoJSON.")
            if geom.geom_type != "Polygon":
                raise ValueError("All geometries must be of type 'Polygon'.")

        # Ensure geometries are valid (no self-intersections, etc.)
        if not gdf.is_valid.all():
            raise ValueError("One or more geometries are invalid.")

        return gdf

    except Exception as e:
        raise ValueError(f"Invalid GeoJSON: {str(e)}")
