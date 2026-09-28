"""SQLAlchemy models for the Document QA Agent."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Document(Base):
    """Document storage model."""

    __tablename__ = "documents"

    id = Column(String(256), primary_key=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # 'pdf' or 'docx'
    language = Column(String(10), nullable=False)  # 'de' or 'zh_CN'
    language_confidence = Column(Float, nullable=True)
    total_pages = Column(Integer, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_status = Column(String(50), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)
    hash = Column(String(64), unique=True, nullable=True)

    # Relationships
    processing_results = relationship("ProcessingResult", back_populates="document")
    formatting_issues = relationship("FormattingIssue", back_populates="document")
    language_issues = relationship("LanguageIssue", back_populates="document")
    reports = relationship("Report", back_populates="document")


class ProcessingResult(Base):
    """Processing results cache model."""

    __tablename__ = "processing_results"

    id = Column(String(256), primary_key=True)
    document_id = Column(String(256), ForeignKey("documents.id"), nullable=False)
    content_extracted = Column(Text, nullable=True)
    document_metadata = Column(JSON, nullable=True)
    extraction_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="processing_results")


class FormattingIssue(Base):
    """Formatting issues model."""

    __tablename__ = "formatting_issues"

    id = Column(String(256), primary_key=True)
    document_id = Column(String(256), ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    issue_type = Column(String(50), nullable=False)  # 'font', 'size', 'heading', etc.
    severity = Column(String(20), nullable=False)  # 'critical', 'warning', 'info'
    location_description = Column(String(255), nullable=True)
    issue_description = Column(Text, nullable=False)
    recommended_fix = Column(Text, nullable=True)
    coordinates = Column(JSON, nullable=True)  # x, y, width, height
    detected_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="formatting_issues")


class LanguageIssue(Base):
    """Language-specific issues model."""

    __tablename__ = "language_issues"

    id = Column(String(256), primary_key=True)
    document_id = Column(String(256), ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    language = Column(String(10), nullable=False)  # 'de' or 'zh_CN'
    rule_violated = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    context = Column(Text, nullable=True)  # Example text from document
    suggested_replacement = Column(String(255), nullable=True)
    issue_description = Column(Text, nullable=False)
    detected_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="language_issues")


class StyleRule(Base):
    """Style rules model."""

    __tablename__ = "style_rules"

    id = Column(String(256), primary_key=True)
    rule_name = Column(String(255), nullable=False)
    language = Column(String(10), nullable=True)  # NULL = applies to all
    scope = Column(String(50), nullable=False)  # 'formatting', 'language', 'structure'
    enabled = Column(Integer, default=1, nullable=False)  # SQLite uses int for bool
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    rule_definition = Column(JSON, nullable=True)
    examples = Column(JSON, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """Report model."""

    __tablename__ = "reports"

    id = Column(String(256), primary_key=True)
    document_id = Column(String(256), ForeignKey("documents.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # 'summary', 'detailed'
    generation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_issues = Column(Integer, default=0, nullable=False)
    critical_count = Column(Integer, default=0, nullable=False)
    warning_count = Column(Integer, default=0, nullable=False)
    info_count = Column(Integer, default=0, nullable=False)
    report_data = Column(JSON, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="reports")
