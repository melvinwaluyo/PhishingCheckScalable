from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship

from app.db import Base

class PhishingResult(Base):
    __tablename__ = "phishingresult"

    phishingresultID = Column(Integer, primary_key=True, autoincrement=True)
    textInput = Column(Text, nullable=False)
    accuracy = Column(Float, nullable=False)
    verdict = Column(String(20), nullable=False)