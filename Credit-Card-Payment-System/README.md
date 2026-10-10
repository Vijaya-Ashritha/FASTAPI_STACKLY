# Credit Card Payment System

## 1. Project Overview

The Credit Card Payment System is a backend application developed using Django, Django REST Framework, FastAPI, and MySQL. It supports user authentication, card management, simulated payments, and transaction history.

## 2. Technologies Used

- Python
- Django and Django REST Framework
- FastAPI
- MySQL
- JWT Authentication
- Postman
- Pytest / Django Test Framework
- Coverage.py

## 3. Main Features

- User registration, login, and logout
- JWT-based authentication and protected APIs
- Add, view, and delete saved cards
- Store masked card numbers and last four digits only
- Simulate successful and failed payments
- View and filter transaction history
- Export transactions to CSV through Django Admin
- View daily payment summaries
- API documentation using Swagger UI

## 4. Project Setup

### Step 1: Create and activate virtual environment

powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1


### Step 2: Install dependencies

powershell
pip install -r requirements.txt


### Step 3: Configure environment variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=credit_card_db
DB_USER=root
DB_PASSWORD=VA3095
DB_HOST=127.0.0.1
DB_PORT=3306


### Step 4: Create the MySQL database

sql
CREATE DATABASE credit_card_db;


### Step 5: Apply database migrations

powershell
python manage.py makemigrations cards transactions
python manage.py migrate


### Step 6: Create an admin account

powershell
python manage.py createsuperuser


### Step 7: Start Django

powershell
python manage.py runserver


### Step 8: Start FastAPI

Open a second PowerShell terminal, activate the same virtual environment, and run:

powershell
uvicorn payment_api.main:app --reload --port 8001


## 5. API Documentation

### Django

- Swagger UI: http://127.0.0.1:8000/api/docs/
- Django Admin: http://127.0.0.1:8000/admin/
- API Schema: http://127.0.0.1:8000/api/schema/

### FastAPI

- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

## 6. Important API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register/ | Register a user |
| POST | /api/token/ | Login and obtain JWT tokens |
| POST | /api/token/refresh/ | Refresh an access token |
| GET | /api/auth/me/ | View logged-in user details |
| POST | /api/auth/logout/ | Log out using a refresh token |
| GET, POST | /api/cards/ | View and add cards |
| DELETE | /api/cards/{id}/ | Delete a saved card |
| GET | /api/transactions/ | View transaction history |
| GET | /api/transactions/{id}/ | View a transaction |
| POST | /payments | Simulate a payment |

## 7. Database Schema

### Users
Stores user account details and password hashes managed by Django.

### Cards
Stores the user relationship, card type, cardholder name, masked card number, last four digits, and creation time.

### Transactions
Stores the user, associated card, amount, status, unique reference, description, and timestamps.

### Admin Logs
Stores administrative actions, details, and timestamps.

## 8. Security

- Passwords are hashed using Django's password management system.
- JWT authentication protects private API endpoints.
- Card numbers are masked before storage.
- CVV values are not stored.
- Django ORM helps protect database operations against SQL injection.
- Input validation is handled through serializers and Pydantic schemas.
- Payment processing is simulated and does not contact a real bank or payment gateway.

## 9. Testing

Run the Django tests:

powershell
python manage.py test transactions


Measure test coverage:

powershell
coverage run manage.py test transactions
coverage report -m
coverage html


Open `htmlcov/index.html` to view the coverage report. The target is at least 50% test coverage.

Test areas include authentication, card management, card masking, transaction history, and payment processing.

## 10. Postman Collection

Import the Postman collection into Postman and configure the Django and FastAPI base URLs. Test registration, login, card operations, payment scenarios, and transaction history.

Save the collection inside the project under:

`postman/credit-card-payment-system.postman_collection.json`

## 11. Screenshots

Add screenshots showing:

- Django Swagger UI
- FastAPI Swagger UI
- Successful registration and login
- Card masking in API responses
- Successful and failed payment responses
- Transaction history
- Django Admin daily payment summary
- Test results and coverage report

## 12. Git Workflow

powershell

git add .
git status
git commit -m "Add credit card payment system documentation and tests"
git push origin main


## 13. Conclusion

This project demonstrates authentication, secure card management, simulated payment processing, transaction tracking, API documentation, automated testing, and database integration using Django, FastAPI, and MySQL.