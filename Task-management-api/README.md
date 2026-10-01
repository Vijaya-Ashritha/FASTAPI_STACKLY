\# Task Management API



A beginner-friendly REST API built using FastAPI to manage tasks. The API supports CRUD operations, input validation, filtering, SQLite database storage, Swagger UI testing, and Postman testing.



\## Technologies Used



\* Python

\* FastAPI

\* Pydantic

\* SQLite

\* Uvicorn

\* Swagger UI

\* Postman



\## Project Structure



```text

Task-management-api/

│

├── app/

│   ├── \_\_init\_\_.py

│   ├── database.py

│   ├── main.py

│   ├── schemas.py

│   │

│   └── routes/

│       ├── \_\_init\_\_.py

│       └── task.py

│

├── README.md

└── requirements.txt

```



\## Features



\* Create a task

\* Get all tasks

\* Get a task by ID

\* Update a task

\* Delete a task

\* Filter tasks by status

\* Filter tasks by priority

\* Search tasks by assigned person

\* Pydantic input validation

\* Enum validation for priority and status

\* Date validation

\* SQLite database storage

\* Proper HTTP status codes

\* Exception handling

\* Swagger UI testing

\* Postman testing



\## Task Fields



Each task contains:



\* Task ID

\* Task Title

\* Description

\* Priority

\* Status

\* Due Date

\* Assigned To

\* Created Date



\## Validation Rules



\### Priority



The priority must be one of:



\* Low

\* Medium

\* High



\### Status



The status must be one of:



\* Pending

\* In Progress

\* Completed



\### Mandatory Fields



The following fields are required:



\* Task ID

\* Task Title

\* Description

\* Priority

\* Status

\* Due Date

\* Assigned To



\## API Endpoints



| Method | Endpoint           | Description    |

| ------ | ------------------ | -------------- |

| POST   | `/tasks/`          | Create a task  |

| GET    | `/tasks/`          | Get all tasks  |

| GET    | `/tasks/{task\_id}` | Get task by ID |

| PUT    | `/tasks/{task\_id}` | Update a task  |

| DELETE | `/tasks/{task\_id}` | Delete a task  |



\## Filtering APIs



\### Filter by Status



```text

GET /tasks/?status=Pending

```



\### Filter by Priority



```text

GET /tasks/?priority=High

```



\### Search by Assigned Person



```text

GET /tasks/?assigned\_to=John

```



\### Get Completed Tasks



```text

GET /tasks/?status=Completed

```



\## Sample Request



\### Create Task



```json

{

&#x20;   "task\_id": 1,

&#x20;   "task\_title": "Complete FastAPI Project",

&#x20;   "description": "Develop Task Management API",

&#x20;   "priority": "High",

&#x20;   "status": "Pending",

&#x20;   "due\_date": "2026-10-15",

&#x20;   "assigned\_to": "John"

}

```



\## HTTP Status Codes



| Status Code | Meaning                   |

| ----------- | ------------------------- |

| 200         | Successful request        |

| 201         | Task created successfully |

| 400         | Bad request               |

| 404         | Task not found            |

| 422         | Validation error          |



\## Error Handling



The API returns a proper error message when a task is not found.



Example:



```json

{

&#x20;   "detail": "Task not found"

}

```



The API also uses Pydantic validation to handle invalid input such as:



\* Invalid priority

\* Invalid status

\* Invalid date

\* Missing mandatory fields



\## Database



The project uses SQLite to store task information.



The database file is created automatically when the application starts.



Database file:



```text

tasks.db

```



\## Installation



Clone or download the project and open the project folder.



If using `uv`, install the required packages:



```powershell

uv add fastapi uvicorn pydantic

```



\## Running the Application



Run the following command:



```powershell

uv run uvicorn app.main:app --reload

```



The application will run at:



```text

http://127.0.0.1:8000

```



\## Swagger UI



FastAPI provides automatic API documentation using Swagger UI.



Open:



```text

http://127.0.0.1:8000/docs

```



Swagger UI can be used to test:



\* Create Task

\* Get Tasks

\* Get Task by ID

\* Update Task

\* Delete Task

\* Filtering APIs



\## Postman Testing



The APIs can also be tested using Postman.



The following scenarios should be tested:



1\. Create a task

2\. Get all tasks

3\. Get task by ID

4\. Update a task

5\. Delete a task

6\. Filter tasks by status

7\. Filter tasks by priority

8\. Search tasks by assigned person

9\. Create task with invalid priority

10\. Create task with invalid status

11\. Create task without mandatory fields

12\. Get a non-existing task

13\. Update a non-existing task

14\. Delete a non-existing task



\## Learning Concepts



This project demonstrates the following concepts:



\* FastAPI

\* REST API

\* CRUD operations

\* Pydantic validation

\* SQLite database

\* Request body

\* Path parameters

\* Query parameters

\* Response models

\* Enum validation

\* Date validation

\* HTTP status codes

\* Exception handling

\* Filtering

\* Swagger UI

\* Postman



\## Conclusion



The Task Management API provides a simple way to create, read, update, delete, and filter tasks. FastAPI is used for building the REST API, Pydantic is used for data validation, and SQLite is used for storing task data.



