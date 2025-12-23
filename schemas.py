from pydantic import BaseModel

class CourseBase(BaseModel):
    course_code: str
    course_name: str
    instructor: str
    credits: int

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True
