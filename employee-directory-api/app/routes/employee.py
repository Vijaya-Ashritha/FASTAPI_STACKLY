
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate

router = APIRouter(prefix="/employees", tags= ["Employees"])

#ADD EMPLOYEE
@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(employee: EmployeeCreate):
    connection = get_connection()

    existing_employee = connection.execute(
        "SELECT * FROM employees WHERE email = ?",(employee.email,),
    ).fetchone()

    if existing_employee:
        connection.close()
        raise HTTPException(
            status_code=409,
            detail= "Email already exists",
        )

    created_at = datetime.now(timezone.utc).isoformat()

    cursor = connection.execute(
        """
        INSERT INTO employees
        (name, email, phone, department, designation, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            employee.name,
            employee.email,
            employee.phone,
            employee.department,
            employee.designation,
            created_at,
        ),
    )

    connection.commit()

    employee_id = cursor.lastrowid

    employee = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,),
    ).fetchone()

    connection.close()

    return dict(employee)

#GET ALL EMPLOYEES
@router.get("", response_model=list[EmployeeResponse])
def get_all_employees():
    connection = get_connection()

    employees = connection.execute(
        "SELECT * FROM employees"
    ).fetchall()

    connection.close()

    return [dict(employee) for employee in employees]

#GET EMPLOYEE BY ID
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int):
    connection = get_connection()

    employee = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,),
    ).fetchone()

    connection.close()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail= "Employee not found",
        )
    return dict(employee)

#UPDATE EMPLOYEE
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee: EmployeeUpdate):
    connection = get_connection()

    existing_employee = connection.execute(
        "SELECT * FROM employees WHERE id =?",
        (employee_id,),
    ).fetchone()

    if existing_employee is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    email_exists = connection.execute(
        "SELECT * FROM employees WHERE email = ? AND id != ?",
        (employee.email, employee_id),
    ).fetchone()

    if email_exists:
        connection.close()
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    connection.execute(
        """
        UPDATE employees
        SET name = ?,
            email = ?,
            phone = ?,
            department = ?,
            designation = ?
        WHERE id = ?
        """,
        (employee.name,
         employee.email,
         employee.phone,
         employee.department,
         employee.designation,
         employee_id,
        ),
    )
    connection.commit()

    updated_employee = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,),
    ).fetchone()

    connection.close()
    return dict(updated_employee)

#DELTED EMPLOYEE
@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int):
    connection = get_connection()

    employee = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,),
    ).fetchone()

    if employee is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    connection.execute(
        "DELETE FROM employees WHERE id =?",
        (employee_id,),
    )
    connection.commit()
    connection.close()



