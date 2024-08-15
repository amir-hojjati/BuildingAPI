# app/api/endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import BuildingLimit, HeightPlateau, SplitBuildingLimit
from app.tools import split_limits, store_processed_splits
from app.core.config import get_db

router = APIRouter()


@router.post("/create-project")
def create_building_limit_splits(project_id: int, building_limits: dict, height_plateaus: dict,
                                 db: Session = Depends(get_db)):
    """
    Creates a new project with building limits and height plateaus,
     splits the limits based on the plateaus and stores everything.

    :param project_id: Unique project identifier
    :param building_limits: GeoJSON data for building limits
    :param height_plateaus: GeoJSON data for height plateaus
    :param db: Database session
    :return: Success message
    """
    try:
        # Check if project exists
        existing_limits = db.query(BuildingLimit).filter(BuildingLimit.project_id == project_id).all()
        existing_plateaus = db.query(HeightPlateau).filter(HeightPlateau.project_id == project_id).all()

        if existing_limits or existing_plateaus:
            raise HTTPException(status_code=409,
                                detail="Project with this ID already has data. Consider updating instead of creating new data.")

        # Perform the split operation and get the original dataframes
        split_gdf, building_limits_gdf, height_plateaus_gdf = split_limits(building_limits, height_plateaus)

        # Persist the original building limits and height plateaus
        for feature in building_limits['features']:
            new_limit = BuildingLimit(project_id=project_id, geometry=feature['geometry'])
            db.add(new_limit)

        for feature in height_plateaus['features']:
            new_plateau = HeightPlateau(project_id=project_id, geometry=feature['geometry'],
                                        elevation=feature['properties']['elevation'])
            db.add(new_plateau)
        db.commit()  # Commit to get the generated IDs

        # Retrieve the IDs after committing
        stored_limits = db.query(BuildingLimit).filter_by(project_id=project_id).all()
        stored_plateaus = db.query(HeightPlateau).filter_by(project_id=project_id).all()

        store_processed_splits(db, split_gdf, project_id, stored_limits, stored_plateaus)

        return {"message": "Successfully split and stored the results"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/update-project")
def update_building_limit_splits(project_id: int, building_limits: dict = None, height_plateaus: dict = None,
                                 db: Session = Depends(get_db)):
    """
    Updates existing building limits and height plateaus for a project, then recomputes the splits.

    :param project_id: Unique project identifier
    :param building_limits: GeoJSON data for building limits (optional)
    :param height_plateaus: GeoJSON data for height plateaus (optional)
    :param db: Database session
    :return: Success message
    """
    if not building_limits and not height_plateaus:
        return {"message": "No new data provided"}
    try:
        # Check if the project exists
        existing_limits = db.query(BuildingLimit).filter(BuildingLimit.project_id == project_id).first()
        existing_plateaus = db.query(HeightPlateau).filter(HeightPlateau.project_id == project_id).first()

        if not existing_limits and not existing_plateaus:
            raise HTTPException(status_code=404, detail="Project with this ID does not exist.")

        # Delete old splits
        db.query(SplitBuildingLimit).filter(SplitBuildingLimit.project_id == project_id).delete()
        db.commit()

        # Prepare updates
        if building_limits:
            limit_ids = [feature['id'] for feature in building_limits['features']]
            limit_versions = {feature['id']: feature['version'] for feature in building_limits['features']}
            limits_to_update = db.query(BuildingLimit).filter(
                BuildingLimit.project_id == project_id,
                BuildingLimit.id.in_(limit_ids)
            ).all()

            # Check for version conflicts and apply updates
            for limit in limits_to_update:
                if limit_versions[limit.id] != limit.version:
                    raise HTTPException(status_code=409,
                                        detail=f"Conflict detected: The building limit with ID {limit.id} has been modified by another user.")
                for feature in building_limits['features']:
                    if feature['id'] == limit.id:
                        limit.geometry = feature['geometry']
                        limit.version += 1

        if height_plateaus:
            plateau_ids = [feature['id'] for feature in height_plateaus['features']]
            plateau_versions = {feature['id']: feature['version'] for feature in height_plateaus['features']}
            plateaus_to_update = db.query(HeightPlateau).filter(
                HeightPlateau.project_id == project_id,
                HeightPlateau.id.in_(plateau_ids)
            ).all()

            # Check for version conflicts and apply updates
            for plateau in plateaus_to_update:
                if plateau_versions[plateau.id] != plateau.version:
                    raise HTTPException(status_code=409,
                                        detail=f"Conflict detected: The height plateau with ID {plateau.id} has been modified by another user.")
                for feature in height_plateaus['features']:
                    if feature['id'] == plateau.id:
                        plateau.geometry = feature['geometry']
                        plateau.elevation = feature['properties']['elevation']
                        plateau.version += 1

        db.commit()

        # Recompute the split building limits
        updated_limits = db.query(BuildingLimit).filter_by(project_id=project_id).all()
        updated_plateaus = db.query(HeightPlateau).filter_by(project_id=project_id).all()

        limits_geojson = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": limit.geometry, "properties": {}} for limit in updated_limits]
        }
        plateaus_geojson = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": plateau.geometry, "properties": {"elevation": plateau.elevation}} for
                plateau in updated_plateaus]
        }

        split_gdf, building_limits_gdf, height_plateaus_gdf = split_limits(limits_geojson, plateaus_geojson)

        store_processed_splits(db, split_gdf, project_id, updated_limits, updated_plateaus)

        return {"message": "Update and recompute successful"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete-project")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Deletes a project and all associated data.

    :param project_id: Unique project identifier
    :param db: Database session
    :return: Success message
    """
    try:
        existing_limits = db.query(BuildingLimit).filter(BuildingLimit.project_id == project_id).all()
        existing_plateaus = db.query(HeightPlateau).filter(HeightPlateau.project_id == project_id).all()

        if not existing_limits and not existing_plateaus:
            raise HTTPException(status_code=404, detail="Project with this ID does not exist.")

        db.query(SplitBuildingLimit).filter(SplitBuildingLimit.project_id == project_id).delete()
        db.query(BuildingLimit).filter(BuildingLimit.project_id == project_id).delete()
        db.query(HeightPlateau).filter(HeightPlateau.project_id == project_id).delete()

        db.commit()

        return {"message": f"Project ID: {project_id} and all associated data have been successfully deleted."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/building-limits/{project_id}")
def get_building_limits(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieves building limits for a specific project.

    :param project_id: Unique project identifier
    :param db: Database session
    :return: GeoJSON of building limits or a message if no data is found
    """
    limits = db.query(BuildingLimit).filter(BuildingLimit.project_id == project_id).all()
    if limits:
        return {"building_limits": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": limit.geometry,
                        "id": limit.id,
                        "version": limit.version,
                        "name": limit.name
                    }
                    for limit in limits
                ]
            }}
    return {"message": "No data found"}


@router.get("/height-plateaus/{project_id}")
def get_height_plateaus(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieves height plateaus for a specific project.

    :param project_id: Unique project identifier
    :param db: Database session
    :return: GeoJSON of height plateaus or a message if no data is found
    """
    plateaus = db.query(HeightPlateau).filter(HeightPlateau.project_id == project_id).all()
    if plateaus:
        return {"height_plateaus": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": plateau.geometry,
                    "properties": {
                        "elevation": plateau.elevation
                    },
                    "id": plateau.id,
                    "version": plateau.version,
                    "name": plateau.name
                }
                for plateau in plateaus
            ]
        }}
    return {"message": "No data found"}


@router.get("/split-building-limits/{project_id}")
def get_split_building_limits(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieves split building limits for a specific project.

    :param project_id: Unique project identifier
    :param db: Database session
    :return: GeoJSON of split building limits or a message if no data is found
    """
    splits = db.query(SplitBuildingLimit).filter(SplitBuildingLimit.project_id == project_id).all()
    if splits:
        return {"building_limits_splits": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": split.geometry,
                    "properties": {
                        "elevation": split.elevation,
                        "building_limit_id": split.building_limit_id,
                        "height_plateau_id": split.height_plateau_id
                    },
                    "id": split.id,
                    "version": split.version
                }
                for split in splits
            ]
        }}
    return {"message": "No data found"}
