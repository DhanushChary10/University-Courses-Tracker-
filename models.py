from sqlalchemy import Column, Integer, String
from .database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True)
    course_name = Column(String)
    instructor = Column(String)
    credits = Column(Integer)
