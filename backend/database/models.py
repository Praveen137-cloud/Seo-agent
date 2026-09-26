import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Audit(Base):
    __tablename__ = "audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    target_url = Column(String(2048), nullable=False)
    status = Column(String(50), default="pending")  # pending, crawling, analyzing, scoring, ai_processing, completed, failed
    score = Column(Integer, default=0)
    pages_crawled = Column(Integer, default=0)
    max_pages = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    summary_data = Column(JSON, nullable=True)  # Store section scores, summary metrics

    pages = relationship("Page", back_populates="audit", cascade="all, delete-orphan")
    issues = relationship("SEOIssue", back_populates="audit", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="audit", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False)
    url = Column(String(2048), nullable=False)
    title = Column(String(1024), nullable=True)
    status_code = Column(Integer, nullable=True)
    load_time_ms = Column(Float, nullable=True)
    html_size = Column(Integer, nullable=True)
    word_count = Column(Integer, default=0)
    h1_tags = Column(JSON, nullable=True)
    h2_tags = Column(JSON, nullable=True)
    meta_description = Column(Text, nullable=True)
    canonical_url = Column(String(2048), nullable=True)
    is_indexable = Column(Boolean, default=True)
    depth = Column(Integer, default=0)
    crawled_at = Column(DateTime, default=datetime.utcnow)

    audit = relationship("Audit", back_populates="pages")

class SEOIssue(Base):
    __tablename__ = "seo_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False)
    page_url = Column(String(2048), nullable=True)
    category = Column(String(50), nullable=False)  # on_page, technical, content, performance, security
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    issue_code = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommendation_summary = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)

    audit = relationship("Audit", back_populates="issues")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    actionable_steps = Column(JSON, nullable=False)
    suggested_content = Column(JSON, nullable=True)  # e.g. proposed title, meta description, H1, keyword fixes

    audit = relationship("Audit", back_populates="recommendations")
