## StayNest Pro – Hotel, Resort & Room Booking Management Platform

## 1. Project Overview

StayNest Pro is a backend application developed using FastAPI to manage hotels, resorts, rooms, and customer bookings. It provides REST APIs for user authentication, hotel management, room management, gallery images, and booking operations.

The application uses MySQL for database storage and SQLAlchemy ORM for database interactions. Pydantic schemas are used for request validation and response formatting. JWT-based authentication and role-based authorization help control access to protected endpoints.

## 2. Technologies Used

- **Language:** Python
- **Backend Framework:** FastAPI
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Authentication:** JWT
- **API Documentation:** Swagger UI
- **API Testing:** Postman
- **Database Migrations:** Alembic

## 3. Project Structure

```text
StayNest-Pro/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   └── services/
├── alembic/
├── postman/
│   └── StayNest-Pro-Complete-Postman-Collection.json
├── tests/
├── main.py
├── requirements.txt
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

The exact contents of the `app` and `alembic` folders may vary depending on the modules implemented in the project.

## 4. Main Modules

### User Authentication
- User registration and login
- Password hashing
- JWT access-token authentication
- Role-based access control

### Hotel Management
- Create and retrieve hotel records
- Update hotel information
- List and search hotels
- Hotel approval workflow
- Manage hotel gallery images

### Room Management
- Create rooms for hotels
- Retrieve room information
- Update room details
- Delete rooms
- Manage room capacity, pricing, amenities, and active status

### Booking Management
- Create customer bookings
- Validate check-in and check-out dates
- Apply customer access restrictions
- Manage booking-related operations supported by the implemented APIs

## 5. User Roles

The application uses role-based access control. Roles implemented in the project include:

- **CUSTOMER:** Accesses customer booking functionality.
- **HOTEL_OWNER:** Manages hotels and rooms according to authorization rules.
- **HOTEL_STAFF:** Access depends on the permissions implemented in the application.
- **ADMIN:** Performs authorized administrative operations, including hotel approval.

The permissions available for each role depend on the individual API endpoint.

## 6. Prerequisites

Install the following before running the project:

- Python 3.12 or a compatible version
- MySQL Server
- MySQL Workbench (optional)
- Git
- Postman (for API testing)

## 7. Installation and Setup

### Step 1: Open the project folder

```powershell
cd "$env:USERPROFILE\Desktop\FASTAPI_STACKLY\StayNest-Pro"
```

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

### Step 3: Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Configure the required values, such as:

- MySQL database URL
- JWT secret key
- Token expiration settings
- Other application settings required by the project

Do not commit `.env` or expose database passwords and secret keys in GitHub.

### Step 6: Create the database

Create the MySQL database configured for the application. For example:

```sql
CREATE DATABASE staynest_pro;
```

Configure the database username, password, host, and database name in your local environment.

### Step 7: Apply database migrations

If the project uses Alembic migrations, run:

```powershell
alembic upgrade head
```

If migrations are not configured for a particular module, follow that module's database initialization implementation.

## 8. Run the Application

From the project root, activate the virtual environment and run:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The application should be available at:

**Base URL:** `http://127.0.0.1:8000`

### Swagger UI

Open the following URL in your browser to view the available API endpoints and try requests:

http://127.0.0.1:8000/docs

### OpenAPI Schema

http://127.0.0.1:8000/openapi.json

## 9. Postman API Testing

The Postman collection and a local environment template are located in the `postman/` directory.

Collection file: `StayNest-Pro-Complete-Postman-Collection.json`

Environment template: `StayNest-Pro-Local.postman_environment.json`. Import both in Postman, then select the local environment and fill in IDs after creating test records.

### How to import

1. Open Postman.
2. Click **Import**.
3. Select the collection JSON file from the project's `postman/` directory.
4. Open the imported collection.
5. Configure the base URL as `http://127.0.0.1:8000` where required.
6. Log in using an appropriate account and use its access token for protected endpoints.
7. Send requests and review the response status and body.

### Testing notes

- Use a CUSTOMER token for customer-only booking operations.
- Use a HOTEL_OWNER token for authorized owner operations.
- Use an ADMIN token for administrative endpoints.
- Ensure the hotel and room IDs in requests exist in the database.
- Check-in dates must precede check-out dates.
- Some hotel details and search endpoints may return only approved hotels.
- A prepared collection does not mean that every request has been executed or verified.

## 10. Common HTTP Status Codes

| Status Code | Meaning |
|---|---|
| 200 OK | Request completed successfully |
| 201 Created | Resource created successfully |
| 204 No Content | Request succeeded without a response body |
| 400 Bad Request | Request or business-rule validation failed |
| 401 Unauthorized | Authentication is missing or invalid |
| 403 Forbidden | User does not have the required permission |
| 404 Not Found | Requested resource does not exist or is not accessible |
| 422 Unprocessable Entity | Request validation failed |
| 500 Internal Server Error | Unexpected server-side error |

Actual responses depend on the endpoint implementation.

## 11. Security Considerations

- Store passwords using the application's password-hashing implementation.
- Protect private endpoints using authentication and authorization.
- Keep `.env` out of version control.
- Use a strong, unique JWT secret key.
- Never include live access tokens, database passwords, or other secrets in the Postman collection.
- Do not grant administrative privileges to ordinary users merely to bypass authorization checks.

## 12. Future Improvements

Potential improvements include:

- Additional automated API tests
- Booking availability and conflict validation
- Payment integration
- Email notifications
- More comprehensive role-based permissions
- Logging and error monitoring
- Deployment configuration and production security hardening

## 13. Conclusion

StayNest Pro is a FastAPI-based backend project designed to support hotel, room, and booking management through REST APIs. It integrates MySQL, SQLAlchemy, Pydantic, authentication, API documentation, and Postman-based testing workflows.

The functionality available in the application depends on the modules implemented and configured in the project.

## 14. Additional Workflows Added During Final Review

The final-review package adds `app/routes/completion.py` and registers it in `main.py`. These are database-backed baseline workflows built on the project's existing SQLAlchemy models:

- `GET /ready` — checks whether the database can be reached.
- `GET /api/v1/dashboards/customer` — customer booking/favorite/unread-notification counts.
- `GET /api/v1/hotels/{hotel_id}/dashboard` — owner/admin hotel booking and paid-revenue summary.
- `GET /api/v1/analytics/revenue` and `GET /api/v1/analytics/occupancy` — date-range analytics.
- `POST /api/v1/messages/threads`, `GET /api/v1/messages/threads`, and thread message endpoints — participant-restricted messaging and read tracking.
- `PUT /api/v1/hotels/{hotel_id}/location` and `GET /api/v1/locations/nearby-hotels` — stored coordinates and nearby approved-hotel search.
- `GET /api/v1/loyalty/balance`, `POST /api/v1/loyalty/earn/{booking_id}`, and `POST /api/v1/loyalty/redeem` — basic points ledger operations.
- `GET /api/v1/recommendations` and `POST /api/v1/support/answer` — transparent rule-based baseline endpoints, not external AI integrations.
- `POST /api/v1/hotels/{hotel_id}/pricing-rules` and `GET /api/v1/rooms/{room_id}/price-quote` — pricing-rule storage and a price-quote endpoint.
- `GET /api/v1/admin/settings`, `PUT /api/v1/admin/settings/{key}`, and security-event review endpoints — admin-only configuration/security records.
- `POST/GET /api/v1/hotels/{hotel_id}/subscription` — local subscription record assignment/read; recurring Stripe billing is not connected to these endpoints.
- `GET /api/v1/admin/analytics/customers` and `GET /api/v1/admin/analytics/business-intelligence` — booking-derived baseline metrics.

These additional endpoints do not silently substitute for external provider integrations. See `MODULE_STATUS_AND_REMAINING_WORK.md` for a requirement-by-requirement status and the remaining work.

## 15. Validation and Honest Completion Status

Run these commands from the project root after installing the requirements and configuring MySQL:

```powershell
python -m compileall -q main.py app alembic tests
python -m pytest -q
alembic upgrade head
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Then verify `http://127.0.0.1:8000/docs`, `/health`, and `/ready`. Use a test database and Stripe test credentials for payment tests. The source package has been syntax-compiled, but live MySQL migrations, all pytest cases, and every Postman request have not been certified as passing in this packaging environment.

**Important:** this is an expanded functional implementation, not a claim of production-complete delivery for every line of the 50-module specification. Email delivery, password-reset/email-verification workflows, external AI, external maps/attractions, subscription billing, background reminders, full Excel/PDF exports, complete financial reconciliation, and several advanced analytics/fraud workflows still require implementation and/or provider configuration. The status matrix identifies these explicitly.
