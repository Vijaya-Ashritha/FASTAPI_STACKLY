# Product Inventory Management API

## 1. Project Overview

The Product Inventory Management API is a REST API developed using FastAPI, SQLAlchemy ORM, and SQLite.

It manages product categories and products, supports CRUD operations, validates request data, provides filtering and searching, and calculates the total inventory value.

## 2. Technologies Used

- Python 3.12
- FastAPI
- SQLAlchemy ORM
- SQLite
- Pydantic
- Uvicorn
- Postman
- Swagger UI

## 3. Features

- Create, retrieve, update, and delete categories.
- Create, retrieve, update, and delete products.
- Maintain a one-to-many relationship between categories and products.
- Ensure category names are unique.
- Validate mandatory product fields, positive prices, and non-negative quantities.
- Prevent products from referencing non-existing categories.
- Prevent deletion of categories that still contain products.
- Filter products by category and price range.
- Search products by name.
- Retrieve all products belonging to a category.
- Calculate the total inventory value.
- Handle missing records and invalid requests using appropriate HTTP status codes.
- Use a database session dependency with `yield` and close sessions after requests.

## 4. Project Structure


Product-Inventory-Management-API/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── main.py
│   └── routes/
│       ├── __init__.py
│       ├── categories.py
│       └── products.py
├── postman/
│   └── product-inventory-management.postman_collection.json
├── requirements.txt
├── README.md
└── inventory.db


The `inventory.db` file is created automatically when the application initializes the database.

## 5. Installation

Open PowerShell in the project directory.

Create and activate a virtual environment:

powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1


Install the required packages:

powershell
python -m pip install --upgrade pip
pip install -r requirements.txt


## 6. Run the Application

Execute:

powershell
python -m uvicorn app.main:app --reload


The API runs at:

http://127.0.0.1:8000

Swagger UI documentation:

http://127.0.0.1:8000/docs

Alternative API documentation:

http://127.0.0.1:8000/redoc

## 7. Database Design

### Categories table

- `category_id`: Primary key
- `category_name`: Required and unique category name
- `description`: Optional category description
- `created_date`: Category creation date

### Products table

- `product_id`: Primary key
- `product_name`: Required product name
- `description`: Optional product description
- `category_id`: Foreign key referencing categories
- `price`: Required price greater than zero
- `quantity`: Required quantity greater than or equal to zero
- `created_date`: Product creation date
- `updated_date`: Product update date

### Relationship

One category can contain multiple products. Each product must reference an existing category.

## 8. API Endpoints

### Category APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/categories` | Create a category |
| GET | `/categories` | Retrieve all categories |
| GET | `/categories/{category_id}` | Retrieve one category |
| PUT | `/categories/{category_id}` | Update a category |
| DELETE | `/categories/{category_id}` | Delete an empty category |
| GET | `/categories/{category_id}/products` | Retrieve products in a category |

### Product APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/products` | Create a product |
| GET | `/products` | Retrieve all products |
| GET | `/products/{product_id}` | Retrieve one product |
| PUT | `/products/{product_id}` | Update a product |
| DELETE | `/products/{product_id}` | Delete a product |
| GET | `/products/inventory-value` | Calculate inventory value |

### Filtering and searching

Filter by category:


GET /products?category_id=1


Filter by price range:


GET /products?min_price=100&max_price=1000


Search by product name:


GET /products?search=laptop


Combine filters:


GET /products?category_id=1&min_price=100&max_price=1000&search=mouse

## 9. Example Requests

### Create a category

`POST /categories`

```json
{
  "category_name": "Electronics",
  "description": "Electronic products"
}
```

### Create a product

`POST /products`

```json
{
  "product_name": "Laptop",
  "description": "Office laptop",
  "category_id": 1,
  "price": 50000,
  "quantity": 5
}
```

### Update a product

`PUT /products/1`

```json
{
  "price": 45000,
  "quantity": 6
}
```

The update API allows partial updates; omitted fields retain their previous values.

## 10. Inventory Value Calculation

The API calculates:

`Inventory Value = SUM(Product Price × Product Quantity)`

For example:

| Product | Price | Quantity | Value |
|---|---:|---:|---:|
| Laptop | 50,000 | 5 | 250,000 |
| Mouse | 500 | 10 | 5,000 |
| Total | | | 255,000 |

Request:

`GET /products/inventory-value`

Example response:

```json
{
  "total_inventory_value": 255000.0
}
```

The result depends on the products currently stored in the database.

## 11. Validation and Error Handling

- `201 Created`: Category or product created successfully.
- `200 OK`: Successful retrieval or update.
- `204 No Content`: Successful deletion.
- `400 Bad Request`: Product references a non-existing category.
- `404 Not Found`: Requested category or product does not exist.
- `409 Conflict`: Duplicate category name or attempt to delete a category containing products.
- `422 Unprocessable Entity`: Invalid request data, negative price, negative quantity, or invalid price range.

Pydantic validates incoming request data. SQLAlchemy manages database operations and transactions.

## 12. Testing

### Swagger UI

1. Start the application.
2. Open `http://127.0.0.1:8000/docs`.
3. Expand an endpoint.
4. Select **Try it out**.
5. Enter the request data.
6. Select **Execute**.
7. Check the response status code and body.

### Postman

1. Open Postman.
2. Import `postman/product-inventory-management.postman_collection.json`.
3. Start the API server.
4. Run the requests in order.
5. Verify successful responses and expected error responses.

Test category creation, duplicate categories, product creation, CRUD operations, category relationships, filtering, searching, inventory calculations, invalid values, and missing records.

## 13. SQLAlchemy Concepts Used

- Database engine and connection configuration
- Session factory and database sessions
- Declarative base and SQLAlchemy models
- Primary keys and foreign keys
- One-to-many relationships
- Pydantic request and response schemas
- Database session dependency using `yield`
- CRUD operations and database transactions
- Query filtering and aggregate functions
- Exception handling
- SQLite database initialization

## 14. Conclusion

This project demonstrates how to build a modular REST API using FastAPI and SQLAlchemy ORM. It combines database integration, request validation, CRUD operations, relationships, search and filtering, inventory calculations, and API testing through Swagger UI and Postman.