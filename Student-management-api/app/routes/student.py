
from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.schemas import StudentCreate, StudentResponse


router = APIRouter(prefix="/students", tags=["Students"])


# CREATE STUDENT
@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate):
    connection = get_connection()

    existing_student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student.student_id,),
    ).fetchone()

    if existing_student:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Student ID already exists",
        )

    existing_email = connection.execute(
        "SELECT * FROM students WHERE email = ?",
        (student.email,),
    ).fetchone()

    if existing_email:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    connection.execute(
        """
        INSERT INTO students
        (student_id, student_name, email, phone, age, course, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student.student_id,
            student.student_name,
            student.email,
            student.phone,
            student.age,
            student.course,
            student.address,
        ),
    )

    connection.commit()
    connection.close()

    return student


# GET ALL STUDENTS / SEARCH BY COURSE / FILTER BY AGE
@router.get("/", response_model=list[StudentResponse])
def get_students(
    course: str | None = Query(default=None),
    min_age: int | None = Query(default=None),
    max_age: int | None = Query(default=None),
):
    connection = get_connection()

    if course:
        students = connection.execute(
            "SELECT * FROM students WHERE course = ?",
            (course,),
        ).fetchall()

    elif min_age is not None and max_age is not None:
        students = connection.execute(
            "SELECT * FROM students WHERE age BETWEEN ? AND ?",
            (min_age, max_age),
        ).fetchall()

    elif min_age is not None:
        students = connection.execute(
            "SELECT * FROM students WHERE age >= ?",
            (min_age,),
        ).fetchall()

    elif max_age is not None:
        students = connection.execute(
            "SELECT * FROM students WHERE age <= ?",
            (max_age,),
        ).fetchall()

    else:
        students = connection.execute(
            "SELECT * FROM students"
        ).fetchall()

    connection.close()

    return [dict(student) for student in students]


# GET STUDENT BY ID
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    connection = get_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()

    connection.close()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return dict(student)


# UPDATE STUDENT
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate):
    connection = get_connection()

    existing_student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()

    if not existing_student:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    if student.student_id != student_id:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Student ID must match the URL",
        )

    existing_email = connection.execute(
        """
        SELECT * FROM students
        WHERE email = ? AND student_id != ?
        """,
        (student.email, student_id),
    ).fetchone()

    if existing_email:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    connection.execute(
        """
        UPDATE students
        SET student_name = ?,
            email = ?,
            phone = ?,
            age = ?,
            course = ?,
            address = ?
        WHERE student_id = ?
        """,
        (
            student.student_name,
            student.email,
            student.phone,
            student.age,
            student.course,
            student.address,
            student_id,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "student_id": student_id,
        "student_name": student.student_name,
        "email": student.email,
        "phone": student.phone,
        "age": student.age,
        "course": student.course,
        "address": student.address,
    }


# DELETE STUDENT
@router.delete("/{student_id}")
def delete_student(student_id: int):
    connection = get_connection()

    existing_student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()

    if not existing_student:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    connection.execute(
        "DELETE FROM students WHERE student_id = ?",
        (student_id,),
    )

    connection.commit()
    connection.close()

    return {"message": "Student deleted successfully"}
