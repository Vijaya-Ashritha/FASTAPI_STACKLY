\# Expense Management API



\## Overview



The Expense Management API is a REST API developed using FastAPI to manage employee expenses and expense categories. It supports CRUD operations, input validation, filtering, expense total calculation, and category-expense relationship management using SQLite.



\## Technologies Used



\- Python

\- FastAPI

\- Pydantic

\- SQLite

\- Uvicorn

\- Swagger UI

\- Postman



\## Project Structure



Expense-management-api/

│

├── README.md

├── \_\_init\_\_.py

│

├── app/

│   ├── \_\_init\_\_.py

│   ├── main.py

│   ├── database.py

│   ├── schemas.py

│   │

│   └── routes/

│       ├── \_\_init\_\_.py

│       ├── category.py

│       └── expense.py

│

└── postman/

&#x20;   └── expense-management-api.postman\_collection.json





\## Features



\- Create, read, update, and delete expense categories.

\- Create, read, update, and delete employee expenses.

\- Category ID and Expense ID are unique.

\- Category names are unique.

\- Expenses can only be created when the category exists.

\- Amount must be greater than 0.

\- Employee name and description are mandatory.

\- Expense date is validated using Pydantic.

\- Payment method supports Cash, Card, UPI, and Bank Transfer.

\- Expense status supports Pending, Approved, and Rejected.

\- Expenses can be filtered by category, status, payment method, and date range.

\- Total expenses can be calculated.

\- Proper HTTP status codes and error messages are returned.

\- Data is stored in SQLite.



\## Category APIs



| Method | Endpoint | Description |

|---|---|---|

| POST | `/categories/` | Create a category |

| GET | `/categories/` | Get all categories |

| GET | `/categories/{category\_id}` | Get category by ID |

| PUT | `/categories/{category\_id}` | Update category |

| DELETE | `/categories/{category\_id}` | Delete category |



\## Expense APIs



| Method | Endpoint | Description |

|---|---|---|

| POST | `/expenses/` | Create an expense |

| GET | `/expenses/` | Get all expenses |

| GET | `/expenses/{expense\_id}` | Get expense by ID |

| PUT | `/expenses/{expense\_id}` | Update expense |

| DELETE | `/expenses/{expense\_id}` | Delete expense |

| GET | `/expenses/total` | Calculate total expenses |



\## Expense Filters



\### Filter by Category





GET /expenses/?category\_id=1





\### Filter by Status





GET /expenses/?status=Approved





\### Filter by Payment Method





GET /expenses/?payment\_method=UPI





\### Filter by Date Range





GET /expenses/?start\_date=2026-10-01\&end\_date=2026-10-06





\## Category Request Example



json

{

&#x20;   "category\_id": 1,

&#x20;   "category\_name": "Travel",

&#x20;   "description": "Employee travel expenses"

}





\## Expense Request Example



json

{

&#x20;   "expense\_id": 1,

&#x20;   "employee\_name": "Rahul",

&#x20;   "category\_id": 1,

&#x20;   "amount": 1500,

&#x20;   "description": "Travel expense",

&#x20;   "expense\_date": "2026-10-06",

&#x20;   "payment\_method": "UPI",

&#x20;   "status": "Pending"

}





\## Validation Rules



\### Category



\- Category ID must be unique.

\- Category name must be unique.

\- Category name is mandatory.

\- Description is mandatory.



\### Expense



\- Expense ID must be unique.

\- Employee name is mandatory.

\- Category ID is mandatory.

\- Category must already exist.

\- Amount must be greater than 0.

\- Description is mandatory.

\- Expense date must be a valid date.

\- Payment method must be one of:

&#x20; - Cash

&#x20; - Card

&#x20; - UPI

&#x20; - Bank Transfer

\- Status must be one of:

&#x20; - Pending

&#x20; - Approved

&#x20; - Rejected



\## Error Handling



The API returns appropriate error responses for invalid requests.



Examples:





404 - Category not found

404 - Expense not found

400 - Category ID already exists

400 - Category name already exists

400 - Expense ID already exists

400 - Cannot delete category because expenses exist for this category

```



Pydantic validation errors are returned automatically by FastAPI when invalid input is provided.



\## Database



SQLite is used to store the application data.



Two tables are created:



\### Categories Table



\- category\_id

\- category\_name

\- description



\### Expenses Table



\- expense\_id

\- employee\_name

\- category\_id

\- amount

\- description

\- expense\_date

\- payment\_method

\- status

\- created\_date



The `category\_id` in the expenses table creates a relationship with the categories table.



\## Running the Application



Install the required dependencies:



```powershell

uv add fastapi uvicorn pydantic

```



Run the application:



```powershell

uv run uvicorn app.main:app --reload





The API will be available at:





http://127.0.0.1:8000





\## Swagger UI



FastAPI automatically provides Swagger UI.



Open:





http://127.0.0.1:8000/docs





Swagger UI can be used to test all Category and Expense APIs.



\## Postman Testing



The APIs can also be tested using Postman.



The following scenarios should be tested:



1\. Create a category

2\. Get all categories

3\. Get category by ID

4\. Update category

5\. Delete category

6\. Create an expense

7\. Get all expenses

8\. Get expense by ID

9\. Update expense

10\. Delete expense

11\. Filter expenses by category

12\. Filter expenses by status

13\. Filter expenses by payment method

14\. Filter expenses by date range

15\. Calculate total expenses

16\. Create expense with a non-existing category

17\. Create expense with amount 0

18\. Create expense with negative amount

19\. Create expense with invalid payment method

20\. Create expense with invalid status

21\. Create duplicate category

22\. Get a non-existing expense

23\. Get a non-existing category



\## Concepts Covered



\- FastAPI

\- REST API

\- CRUD Operations

\- Pydantic Validation

\- SQLite Database

\- Request Body

\- Path Parameters

\- Query Parameters

\- Response Models

\- Enum Validation

\- Date Validation

\- Filtering

\- Date Range Filtering

\- Business Logic

\- Entity Relationships

\- HTTP Status Codes

\- Exception Handling

\- Swagger UI

\- Postman Testing



\## API Documentation



Once the application is running, API documentation can be accessed through:





http://127.0.0.1:8000/docs





\## Conclusion



The Expense Management API provides a simple and structured way to manage employee expenses and expense categories. It demonstrates CRUD operations, validation, SQLite database operations, entity relationships, filtering, exception handling, and API testing using FastAPI, Swagger UI, and Postman.

