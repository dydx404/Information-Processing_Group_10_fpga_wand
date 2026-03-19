from __future__ import annotations

from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    wand_id = Column(Integer, index=True, nullable=False)
    attempt_id = Column(Integer, nullable=False)
    device_number = Column(Integer, nullable=False)
    start_ms = Column(BigInteger, nullable=False)
    end_ms = Column(BigInteger, nullable=False)
    finalized_at_ms = Column(BigInteger, nullable=False)
    num_points = Column(Integer, nullable=False)
    render_path = Column(Text, nullable=False)
    status = Column(String, default="processed")
    best_template_id = Column(String, nullable=True)
    best_template_name = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TemplateChampion(Base):
    __tablename__ = "template_champions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, unique=True, index=True, nullable=False)
    template_name = Column(String, nullable=False)
    attempt_id = Column(Integer, nullable=False)
    wand_id = Column(Integer, index=True, nullable=False)
    device_number = Column(Integer, nullable=False)
    finalized_at_ms = Column(BigInteger, nullable=False)
    score = Column(Float, nullable=False)
    player_name = Column(String, nullable=True)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
