from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from database import Base


class CandidateDB(Base):
    __tablename__ = "candidate"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    city = Column(String)
    full_address = Column(String)
    skills = Column(String)

