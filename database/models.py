from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class InspectionRecord(Base):
    """Database model for IC inspection records"""
    __tablename__ = 'inspection_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_path = Column(String(500), nullable=False)
    part_number = Column(String(100), nullable=False)
    oem_name = Column(String(100), nullable=False)
    
    # OCR Results
    extracted_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    
    # Verification Results
    status = Column(String(50), nullable=False)  # GENUINE, FAKE, UNCERTAIN
    confidence = Column(Float, nullable=False)
    differences = Column(Text, nullable=True)  # JSON string of differences
    
    # Reference Data
    reference_markings = Column(Text, nullable=True)  # JSON string
    datasheet_url = Column(String(500), nullable=True)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    verified_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<InspectionRecord(id={self.id}, part_number={self.part_number}, status={self.status})>"


class DatasheetCache(Base):
    """Cache for downloaded datasheet information"""
    __tablename__ = 'datasheet_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_number = Column(String(100), nullable=False, unique=True)
    oem_name = Column(String(100), nullable=False)
    datasheet_url = Column(String(500), nullable=True)
    marking_info = Column(Text, nullable=True)  # JSON string
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_valid = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<DatasheetCache(part_number={self.part_number}, oem={self.oem_name})>"
