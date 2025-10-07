from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json

from config import Config
from .models import Base, InspectionRecord, DatasheetCache
from utils import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages database operations for IC inspection system"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or Config.DATABASE_URL
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()
        logger.info(f"Database initialized: {self.database_url}")
    
    def _create_tables(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    # Inspection Record Operations
    
    def save_inspection(self, inspection_data: Dict) -> InspectionRecord:
        """Save an inspection record to the database"""
        session = self.get_session()
        try:
            record = InspectionRecord(
                image_path=inspection_data.get('image_path'),
                part_number=inspection_data.get('part_number'),
                oem_name=inspection_data.get('oem_name'),
                extracted_text=inspection_data.get('extracted_text'),
                ocr_confidence=inspection_data.get('ocr_confidence'),
                status=inspection_data.get('status'),
                confidence=inspection_data.get('confidence'),
                differences=json.dumps(inspection_data.get('differences', [])),
                reference_markings=json.dumps(inspection_data.get('reference_markings', {})),
                datasheet_url=inspection_data.get('datasheet_url'),
                notes=inspection_data.get('notes')
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            logger.info(f"Saved inspection record: {record.id}")
            return record
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving inspection: {e}")
            raise
        finally:
            session.close()
    
    def get_inspection(self, inspection_id: int) -> Optional[InspectionRecord]:
        """Retrieve an inspection record by ID"""
        session = self.get_session()
        try:
            return session.query(InspectionRecord).filter(
                InspectionRecord.id == inspection_id
            ).first()
        finally:
            session.close()
    
    def get_inspections_by_part(self, part_number: str) -> List[InspectionRecord]:
        """Get all inspections for a specific part number"""
        session = self.get_session()
        try:
            return session.query(InspectionRecord).filter(
                InspectionRecord.part_number == part_number
            ).order_by(InspectionRecord.timestamp.desc()).all()
        finally:
            session.close()
    
    def get_recent_inspections(self, limit: int = 10) -> List[InspectionRecord]:
        """Get the most recent inspections"""
        session = self.get_session()
        try:
            return session.query(InspectionRecord).order_by(
                InspectionRecord.timestamp.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    # Datasheet Cache Operations
    
    def get_cached_datasheet(self, part_number: str, max_age_days: int = 30) -> Optional[DatasheetCache]:
        """Retrieve cached datasheet info if not expired"""
        session = self.get_session()
        try:
            cache = session.query(DatasheetCache).filter(
                DatasheetCache.part_number == part_number,
                DatasheetCache.is_valid == True
            ).first()
            
            if cache:
                age = datetime.utcnow() - cache.last_updated
                if age.days > max_age_days:
                    logger.info(f"Cache expired for {part_number}")
                    return None
                logger.info(f"Cache hit for {part_number}")
                return cache
            
            logger.info(f"Cache miss for {part_number}")
            return None
        finally:
            session.close()
    
    def save_datasheet_cache(self, cache_data: Dict) -> DatasheetCache:
        """Save or update datasheet cache"""
        session = self.get_session()
        try:
            # Check if cache exists
            existing = session.query(DatasheetCache).filter(
                DatasheetCache.part_number == cache_data['part_number']
            ).first()
            
            if existing:
                # Update existing cache
                existing.oem_name = cache_data.get('oem_name', existing.oem_name)
                existing.datasheet_url = cache_data.get('datasheet_url')
                existing.marking_info = json.dumps(cache_data.get('marking_info', {}))
                existing.last_updated = datetime.utcnow()
                existing.is_valid = True
                cache = existing
                logger.info(f"Updated cache for {cache_data['part_number']}")
            else:
                # Create new cache
                cache = DatasheetCache(
                    part_number=cache_data['part_number'],
                    oem_name=cache_data['oem_name'],
                    datasheet_url=cache_data.get('datasheet_url'),
                    marking_info=json.dumps(cache_data.get('marking_info', {})),
                    is_valid=True
                )
                session.add(cache)
                logger.info(f"Created cache for {cache_data['part_number']}")
            
            session.commit()
            session.refresh(cache)
            return cache
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving datasheet cache: {e}")
            raise
        finally:
            session.close()
    
    def invalidate_cache(self, part_number: str):
        """Invalidate cached datasheet"""
        session = self.get_session()
        try:
            cache = session.query(DatasheetCache).filter(
                DatasheetCache.part_number == part_number
            ).first()
            if cache:
                cache.is_valid = False
                session.commit()
                logger.info(f"Invalidated cache for {part_number}")
        finally:
            session.close()
