from sqlalchemy import Column, Integer, String, Float, BigInteger, Text, DateTime
from sqlalchemy.sql import func
from .database import Base   # ← note the dot (relative import)


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