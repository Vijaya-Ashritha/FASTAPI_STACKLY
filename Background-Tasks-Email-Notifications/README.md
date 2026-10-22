\# Background Tasks and Email Notifications in FastAPI



\## 1. Project Overview



This project implements background tasks and email notifications in a FastAPI application. It uses SQLAlchemy and MySQL to store user and product information and sends email notifications for important events.



\## 2. Objectives



\- Send an email notification when a new user registers.

\- Notify the administrator when a product reaches its low-stock reorder level.

\- Send notifications for important inventory operations.

\- Execute email tasks using FastAPI BackgroundTasks.

\- Manage database tables using SQLAlchemy and Alembic.



\## 3. Technologies Used



\- Python

\- FastAPI

\- SQLAlchemy

\- MySQL

\- Alembic

\- Pydantic Settings

\- SMTP

\- Postman

\- Swagger UI



\## 4. Project Structure



```text

Background-Tasks-Email-Notifications/

├── app/

│   ├── core/

│   │   └── config.py

│   ├── db/

│   │   └── database.py

│   ├── models/

│   │   ├── user.py

│   │   └── product.py

│   ├── schemas/

│   │   ├── user.py

│   │   └── product.py

│   ├── routers/

│   │   ├── auth.py

│   │   └── products.py

│   ├── services/

│   │   ├── email\_service.py

│   │   └── notification\_service.py

│   ├── tasks/

│   │   └── email\_tasks.py

│   ├── utils/

│   │   └── security.py

│   └── main.py

├── alembic/

├── alembic.ini

├── requirements.txt

├── .env

├── .env.example

├── .gitignore

└── README.md

```



\## 5. Installation and Setup



\### Step 1: Open the project directory



```powershell

cd "$env:USERPROFILE\\Desktop\\FASTAPI\_STACKLY\\Background-Tasks-Email-Notifications"

```



\### Step 2: Activate the virtual environment



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### Step 3: Install dependencies



```powershell

python -m pip install -r requirements.txt

```



\### Step 4: Configure environment variables



Update `.env` with your MySQL connection details and SMTP email credentials.



Never commit `.env` or share passwords and email app passwords.



\### Step 5: Apply database migrations



```powershell

alembic upgrade head

```



\### Step 6: Start the application



```powershell

uvicorn app.main:app --reload

```



\### Step 7: Open Swagger UI



http://127.0.0.1:8000/docs



\## 6. Email Notification Workflow



\### User Registration



1\. A user submits the registration request.

2\. The application validates the input.

3\. The user record is saved in MySQL.

4\. A registration email task is scheduled using BackgroundTasks.

5\. The task attempts to send the email through SMTP.



\### Low-Stock Notification



1\. A product is created or updated.

2\. The application checks the stock quantity against the reorder level.

3\. When the low-stock condition is met, an email task is scheduled.

4\. The notification service prepares the message.

5\. The email service sends the notification through SMTP.



\### Inventory Operation Notification



1\. A supported inventory operation is performed.

2\. The application saves the database changes.

3\. A background email task is scheduled to notify the configured recipient.



\## 7. Testing with Postman



1\. Start the FastAPI server.

2\. Open Postman.

3\. Create a request using the endpoint displayed in Swagger.

4\. Select the correct HTTP method.

5\. Choose \*\*Body → raw → JSON\*\* for JSON requests.

6\. Enter the required request fields.

7\. Click \*\*Send\*\*.

8\. Verify the response and check the application terminal for email errors.

9\. Check the recipient's inbox and spam folder.



Use a new email address for each registration test if duplicate emails are not permitted.



\## 8. Configuration Notes



\- MySQL must be running and accessible.

\- The database configured in `.env` must exist.

\- SMTP credentials must be valid for email delivery.

\- Gmail SMTP commonly requires an App Password when two-step verification is enabled.

\- Verify request paths and JSON fields against Swagger before testing.



\## 9. Important Limitations



FastAPI BackgroundTasks executes work after the response is returned, but it does not provide a persistent task queue or automatic retry mechanism. SMTP failures should be monitored through application logs.



\## 10. Conclusion



This project demonstrates how to integrate FastAPI BackgroundTasks with SQLAlchemy, MySQL, and SMTP to provide asynchronous email notifications for user registration and inventory events.



