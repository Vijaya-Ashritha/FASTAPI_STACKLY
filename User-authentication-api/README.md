\# User Authentication API



\## Project Description



This project is a REST API developed using FastAPI to manage user registration, login, and user information.



The API uses SQLite as the database and bcrypt password hashing to securely store user passwords.



\## Technologies Used



\- Python

\- FastAPI

\- Pydantic

\- SQLite

\- Passlib

\- Bcrypt

\- Uvicorn



\## Project Structure





User-authentication-api/

│

├── app/

│   ├── \_\_init\_\_.py

│   ├── main.py

│   ├── database.py

│   ├── schemas.py

│   │

│   └── routes/

│       ├── \_\_init\_\_.py

│       └── user.py

│

├── postman/

│   └── user-authentication-api.postman\_collection.json

│

├── users.db

├── README.md

├── pyproject.toml

└── uv.lock

```



\## Features



\- User registration

\- User login

\- Get all users

\- Get user by ID

\- Update user details

\- Delete user

\- Change user password

\- Role-based filtering

\- Search users by name

\- Email validation

\- Password minimum length validation

\- Duplicate email validation

\- Password hashing

\- Password verification

\- Exception handling

\- SQLite database integration



\## User Details



Each user contains:



\- User ID

\- Full Name

\- Email

\- Phone Number

\- Password

\- Role

\- Created Date



The available roles are:



\- Admin

\- User



\## API Endpoints



| Method | Endpoint | Description | Status |

|---|---|---|---|

| POST | `/register` | Register a new user | 201 |

| POST | `/login` | Login user | 200 |

| GET | `/users` | Get all users | 200 |

| GET | `/users/{user\_id}` | Get user by ID | 200 |

| PUT | `/users/{user\_id}` | Update user details | 200 |

| DELETE | `/users/{user\_id}` | Delete user | 204 |

| PUT | `/users/{user\_id}/password` | Change password | 200 |



\## Query Parameters



\### Filter by Role





GET /users?role=Admin





Returns users with the Admin role.



\### Search by Name



GET /users?name=John





Returns users whose name contains the given text.



\### Filter by Role and Name





GET /users?role=User\&name=John





Returns users matching both the role and name.



\## Validation



The API performs the following validations:



\- Full name is mandatory.

\- Email is mandatory and must be a valid email address.

\- Password must contain at least 8 characters.

\- Email must be unique.

\- Role must be either `Admin` or `User`.

\- User ID must exist when updating, deleting, or changing a password.



\## Password Security



Passwords are not stored as plain text in the database.



During registration, the password is converted into a bcrypt hash before it is stored in SQLite.



During login, the entered password is verified against the stored password hash.



\## HTTP Status Codes



\- `200 OK` - Request completed successfully.

\- `201 Created` - User successfully registered.

\- `204 No Content` - User successfully deleted.

\- `400 Bad Request` - Invalid request such as duplicate email.

\- `401 Unauthorized` - Invalid email or password.

\- `404 Not Found` - User does not exist.

\- `422 Unprocessable Entity` - Validation error.



\## How to Run the Project



\### Step 1: Open the project folder



powershell

cd C:\\Users\\Administrator\\Desktop\\FASTAPI\_STACKLY\\User-authentication-api





\### Step 2: Install dependencies



powershell

uv sync





\### Step 3: Start the FastAPI server



powershell

uv run uvicorn app.main:app --reload





The API will run at:



http://127.0.0.1:8000





\## Swagger Documentation



Open the following URL in the browser:





http://127.0.0.1:8000/docs





Swagger UI can be used to test all API endpoints.



\## Postman Testing



The project contains a Postman collection with test cases for:



\- Successful user registration

\- Duplicate email

\- Invalid email

\- Weak password

\- Valid login

\- Incorrect password

\- Non-existing email

\- Get all users

\- Get user by ID

\- Update user

\- Delete user

\- Change password

\- Role filtering

\- Name searching



\## Important Security Check



The password should not be returned in API responses.



The database stores the password as a bcrypt hash instead of storing the original password.



\## Database



SQLite is used as the database.



The database file is:





users.db





The database table is:





users





\## Main Concepts Learned



\- FastAPI

\- REST API

\- CRUD operations

\- Pydantic models

\- Request body

\- Path parameters

\- Query parameters

\- SQLite

\- SQL queries

\- Password hashing

\- Password verification

\- Enum validation

\- HTTP status codes

\- Exception handling

\- Swagger documentation

\- Postman API testing

