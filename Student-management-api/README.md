# Student Management API

## Project Description

Student Management API is a REST API developed using FastAPI to manage student information. It provides CRUD operations such as creating, viewing, updating, and deleting student records.

The API uses SQLite for storing student data and Pydantic for input validation.

## Technologies Used

* Python
* FastAPI
* Pydantic
* SQLite
* Uvicorn
* Swagger UI
* Postman

## Student Details

The API manages the following student information:

* Student ID
* Student Name
* Email
* Phone Number
* Age
* Course
* Address

## Features

* Create a new student
* Get all students
* Get a student by ID
* Update student details
* Delete a student
* Search students by course
* Filter students by age
* Validate email
* Validate phone number
* Validate age between 18 and 60
* Prevent duplicate Student IDs
* Prevent duplicate email addresses
* Handle student not found errors

## API Endpoints

| Method | Endpoint                           | Description       |
| ------ | ---------------------------------- | ----------------- |
| POST   | `/students/`                       | Create a student  |
| GET    | `/students/`                       | Get all students  |
| GET    | `/students/{student_id}`           | Get student by ID |
| PUT    | `/students/{student_id}`           | Update student    |
| DELETE | `/students/{student_id}`           | Delete student    |
| GET    | `/students/?course=Python`         | Search by course  |
| GET    | `/students/?min_age=20&max_age=30` | Filter by age     |

## Project Structure


Student-management-API/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   └── routes/
│       ├── __init__.py
│       └── student.py
│
├── students.db
├── README.md
└── pyproject.toml


## Installation

Install the required packages using:


uv add fastapi uvicorn pydantic[email]

## Run the Application

Start the FastAPI application using:


uv run uvicorn app.main:app --reload

The application will run at:


http://127.0.0.1:8000


## Swagger UI

FastAPI provides automatic API documentation using Swagger UI.

Open:


http://127.0.0.1:8000/docs


Swagger can be used to test all the API endpoints.

## Sample Request

### Create Student

**POST `/students/`**

json
{
    "student_id": 1,
    "student_name": "Vijaya",
    "email": "vijaya@gmail.com",
    "phone": "9876543210",
    "age": 22,
    "course": "Python",
    "address": "Visakhapatnam"
}


## Search by Course

To find students studying Python:


GET /students/?course=Python

## Filter by Age

To find students between 20 and 30 years old:


GET /students/?min_age=20&max_age=30


## Validation

The API validates:

* Student name is required
* Email is required and must be valid
* Age is required and must be between 18 and 60
* Course is required
* Phone number must contain 10 digits
* Student ID must be unique
* Email must be unique

## Error Handling

The API returns appropriate error messages for invalid operations.

Examples:

json
{
    "detail": "Student ID already exists"
}


json
{
    "detail": "Email already exists"
}


json
{
    "detail": "Student not found"
}


## Testing

The APIs were tested using:

* Swagger UI
* Postman

The following test cases are covered:

* Create student
* Get all students
* Get student by ID
* Update student
* Delete student
* Search by course
* Filter by age
* Invalid email
* Invalid age
* Duplicate email
* Non-existing student

## HTTP Status Codes

| Status Code | Meaning                      |
| ----------- | ---------------------------- |
| 200         | Successful request           |
| 201         | Student created successfully |
| 400         | Bad request / duplicate data |
| 404         | Student not found            |
| 422         | Validation error             |

## Conclusion

This project demonstrates how to build a basic REST API using FastAPI with SQLite database integration, Pydantic validation, CRUD operations, query parameters, exception handling, and API testing using Swagger UI and Postman.



