# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

Base = declarative_base()

class BuildingLimit(Base):
    __tablename__ = 'building_limits'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False, default=1)
    project_id = Column(Integer, nullable=False)  # Project ID to associate data with a specific project
    geometry = Column(JSON, nullable=False)
    name = Column(String, nullable=True, default=f'limit-0')

    __table_args__ = (UniqueConstraint('project_id', 'id', name='_building_limit_uc'),)

class HeightPlateau(Base):
    __tablename__ = 'height_plateaus'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False, default=1)
    project_id = Column(Integer, nullable=False)
    elevation = Column(Float, nullable=False)
    geometry = Column(JSON, nullable=False)
    name = Column(String, nullable=True, default=f'plat-0')

    __table_args__ = (UniqueConstraint('project_id', 'id', name='_height_plateau_uc'),)

class SplitBuildingLimit(Base):
    __tablename__ = 'split_building_limits'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False, default=1)
    project_id = Column(Integer, nullable=False)
    elevation = Column(Float, nullable=False)
    geometry = Column(JSON, nullable=False)
    building_limit_id = Column(Integer, ForeignKey('building_limits.id'), nullable=False)
    height_plateau_id = Column(Integer, ForeignKey('height_plateaus.id'), nullable=False)

    building_limit = relationship('BuildingLimit')
    height_plateau = relationship('HeightPlateau')

    __table_args__ = (UniqueConstraint('project_id', 'id', name='_split_building_limit_uc'),)
