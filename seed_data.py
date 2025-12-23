from backend.database import SessionLocal, engine
from backend.models import Base, Course
import random

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
db.query(Course).delete()
db.commit()

# Instructor-wise distribution (TOTAL = 20 courses)
instructor_distribution = {
    "Dr Instructor 1": 5,
    "Dr Instructor 2": 4,
    "Dr Instructor 3": 4,
    "Dr Instructor 4": 3,
    "Dr Instructor 5": 2,
    "Dr Instructor 6": 2,
}

course_no = 1

for instructor, count in instructor_distribution.items():
    for _ in range(count):
        course = Course(
            course_code=f"CS{course_no:03}",
            course_name=f"Course {course_no}",
            instructor=instructor,
            credits=random.randint(1, 5)
        )
        db.add(course)
        course_no += 1

db.commit()
db.close()

print("✅ 20 COURSES INSERTED WITH CONTROLLED INSTRUCTOR DISTRIBUTION")
