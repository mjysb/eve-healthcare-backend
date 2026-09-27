# EVE Healthcare Backend

Backend service for diagnostic test bookings and simulated payments, built as part of the EVE Healthcare SDE Intern — Backend Engineering Assignment.

## Overview

This project provides REST APIs for:

- User signup and login
- JWT-based authentication
- Diagnostic centres and diagnostic tests
- Diagnostic test bookings
- Simulated payment processing
- Payment status webhooks
- Idempotent webhook handling
- Authorization and validation checks
- Automated API testing

The backend is built using FastAPI and PostgreSQL.

---

## Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **Password Hashing:** bcrypt
- **API Documentation:** Swagger / OpenAPI
- **Testing:** Pytest
- **HTTP Testing:** FastAPI TestClient

---

# Features

## 1. Authentication

The application supports:

- User signup
- User login
- Password hashing using bcrypt
- JWT-based authentication
- Protected endpoints using Bearer tokens
- Authentication validation for protected resources

### Authentication Flow

```text
User
  |
  | POST /signup
  v
Create account
  |
  | POST /login
  v
JWT access token
  |
  | Authorization: Bearer <token>
  v
Protected API endpoints
```

---

## 2. Diagnostic Centres and Tests

The application supports creating and retrieving diagnostic centres and diagnostic tests.

A diagnostic centre contains:

- Centre name
- Location

A diagnostic test contains:

- Test name
- Price
- Centre ID

Each diagnostic test belongs to a diagnostic centre.

---

## 3. Booking System

Authenticated users can create diagnostic test bookings.

A booking contains:

- User
- Diagnostic test
- Diagnostic centre
- Appointment date/time
- Amount
- Booking status

The booking amount is obtained from the price of the selected diagnostic test rather than being supplied directly by the client.

### Booking Statuses

The application uses:

```text
PENDING
CONFIRMED
FAILED
```

`PENDING` is the initial state of a newly created booking.

A successful payment changes the booking status to `CONFIRMED`.

A failed payment webhook changes the booking status to `FAILED`.

---

## 4. Simulated Payment

No real payment gateway is integrated.

The endpoint:

```text
POST /payments
```

simulates payment processing for an authenticated user's booking.

For a successful simulated payment:

```text
Booking: PENDING
        |
        | Payment
        v
Payment: SUCCESS
        |
        v
Booking: CONFIRMED
```

The payment amount is derived from the booking amount.

The API also prevents users from processing payments for bookings belonging to another user.

---

## 5. Payment Webhook

The application provides:

```text
POST /payments/webhook
```

The webhook accepts:

- `event_id`
- `booking_id`
- `status`

Supported payment statuses are:

```text
SUCCESS
FAILED
```

### Successful webhook

```text
Webhook SUCCESS
       |
       v
Booking → CONFIRMED
```

### Failed webhook

```text
Webhook FAILED
       |
       v
Booking → FAILED
```

---

## 6. Webhook Idempotency

Webhook processing is designed to be idempotent.

Each webhook contains a unique `event_id`.

Before processing a webhook, the application checks whether that event has already been processed.

If the same event is received again, it is not processed a second time.

Example:

```text
First request
event_id = event-001
        |
        v
Webhook processed
        |
        v
Booking updated


Second request
event_id = event-001
        |
        v
Already processed
        |
        v
No duplicate processing
```

This prevents repeated webhook events from creating duplicate payment records or repeatedly modifying booking state.

---

# API Endpoints

| Method | Endpoint | Authentication | Description |
|---|---|---|---|
| GET | `/` | No | Health check |
| POST | `/signup` | No | Create a user |
| POST | `/login` | No | Login and receive JWT |
| GET | `/me` | Yes | Get authenticated user |
| POST | `/centres` | Yes | Create diagnostic centre |
| GET | `/centres` | No | List diagnostic centres |
| POST | `/tests` | Yes | Create diagnostic test |
| GET | `/tests` | No | List diagnostic tests |
| POST | `/bookings` | Yes | Create diagnostic booking |
| POST | `/payments` | Yes | Process simulated payment |
| POST | `/payments/webhook` | No | Process payment status webhook |

---

# Example API Requests

## 1. Health Check

### Request

```http
GET /
```

### Response

```json
{
  "message": "EVE Healthcare Backend is running"
}
```

---

## 2. Signup

### Request

```http
POST /signup
Content-Type: application/json
```

```json
{
  "name": "Test User",
  "email": "testuser@example.com",
  "password": "testpassword123"
}
```

### Response

```json
{
  "message": "User created successfully"
}
```

---

## 3. Login

### Request

```http
POST /login
Content-Type: application/json
```

```json
{
  "email": "testuser@example.com",
  "password": "testpassword123"
}
```

### Response

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

The returned JWT is used for protected endpoints.

Example:

```http
Authorization: Bearer <JWT_TOKEN>
```

---

## 4. Create Diagnostic Centre

### Request

```http
POST /centres
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "name": "Apollo Diagnostics",
  "location": "Delhi"
}
```

---

## 5. Create Diagnostic Test

### Request

```http
POST /tests
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "name": "CBC",
  "price": 500,
  "centre_id": 1
}
```

---

## 6. Create Booking

### Request

```http
POST /bookings
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "test_id": 1,
  "centre_id": 1,
  "appointment_datetime": "2026-10-10T10:00:00"
}
```

### Initial booking state

```json
{
  "status": "PENDING"
}
```

The booking amount is taken from the diagnostic test price.

---

## 7. Process Simulated Payment

### Request

```http
POST /payments
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "booking_id": 1
}
```

### Successful response

```json
{
  "message": "Payment processed successfully",
  "payment_id": 1,
  "booking_id": 1,
  "amount": 500.0,
  "payment_status": "SUCCESS",
  "booking_status": "CONFIRMED"
}
```

---

## 8. Payment Webhook

### Request

```http
POST /payments/webhook
Content-Type: application/json
```

```json
{
  "event_id": "event-001",
  "booking_id": 1,
  "status": "SUCCESS"
}
```

### Example failed payment webhook

```json
{
  "event_id": "event-002",
  "booking_id": 2,
  "status": "FAILED"
}
```

The corresponding booking is updated to:

```text
FAILED
```

---

# Database Design

PostgreSQL is used as the relational database.

The application contains five main tables:

```text
users
  |
  | 1-to-many
  v
bookings
  | \
  |  \
  |   \
  v    v
tests  diagnostic_centres
  |
  |
  v
diagnostic_centres


bookings
  |
  | 1-to-many
  v
payments
```

## Tables

### 1. users

Stores registered users.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | User name |
| `email` | String | Unique user email |
| `password_hash` | String | Hashed password |
| `created_at` | DateTime | Account creation time |

---

### 2. diagnostic_centres

Stores diagnostic centre information.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | Diagnostic centre name |
| `location` | String | Centre location |

---

### 3. diagnostic_tests

Stores diagnostic tests offered by centres.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | Diagnostic test name |
| `price` | Float | Test price |
| `centre_id` | Integer | Foreign key to diagnostic centre |

Relationship:

```text
diagnostic_centres 1 ---- N diagnostic_tests
```

---

### 4. bookings

Stores user test bookings.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `user_id` | Integer | Foreign key to users |
| `test_id` | Integer | Foreign key to diagnostic tests |
| `centre_id` | Integer | Foreign key to diagnostic centres |
| `appointment_datetime` | DateTime | Appointment date/time |
| `amount` | Float | Booking amount |
| `status` | String | Booking status |
| `created_at` | DateTime | Booking creation time |

Relationships:

```text
users 1 ---- N bookings

diagnostic_tests 1 ---- N bookings

diagnostic_centres 1 ---- N bookings
```

---

### 5. payments

Stores simulated payment information.

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `booking_id` | Integer | Foreign key to bookings |
| `amount` | Float | Payment amount |
| `status` | String | Payment status |
| `event_id` | String | Unique webhook event ID |
| `created_at` | DateTime | Payment creation time |

The `event_id` is unique and is used to support webhook idempotency.

---

# Database Initialization

The database tables can be created using:

```bash
python init_db.py
```

The application uses SQLAlchemy to create the database tables.

For this assignment, database migrations such as Alembic have not been added.

---

# Project Structure

```text
eve-healthcare-backend/
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── diagnostic_centre.py
│   ├── diagnostic_test.py
│   ├── booking.py
│   └── payment.py
│
├── tests/
│   └── test_api.py
│
├── .gitignore
├── auth.py
├── database.py
├── init_db.py
├── main.py
├── schemas.py
├── requirements.txt
└── README.md
```

---

# Running the Project Locally

## 1. Clone the repository

```bash
git clone <repository-url>
cd eve-healthcare-backend
```

---

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Set up PostgreSQL

Install PostgreSQL and create a database named:

```text
eve_healthcare
```

Update the database connection string in `database.py` according to the local PostgreSQL username and configuration.

Example:

```python
DATABASE_URL = "postgresql+psycopg://username@localhost/eve_healthcare"
```

---

## 5. Initialize database tables

Run:

```bash
python init_db.py
```

Expected output:

```text
Database tables created successfully!
```

---

## 6. Start the FastAPI server

Run:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Swagger / OpenAPI Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to manually test the APIs.

For protected endpoints:

1. Call `/login`
2. Copy the returned JWT token
3. Click **Authorize** in Swagger
4. Enter:

```text
Bearer <JWT_TOKEN>
```

5. Test the protected endpoints.

---

# Testing

The project includes automated API tests using Pytest.

Run:

```bash
pytest -v
```

The test suite currently covers:

- Health check
- User signup
- User login
- Authentication without a token
- Authentication with a valid token
- Booking creation
- Successful payment
- Invalid booking payment
- Payment for another user's booking
- Webhook idempotency
- Failed payment webhook
- Invalid webhook status

The current test suite contains **13 automated tests**.

Expected result:

```text
13 passed
```

---

# Edge Cases Handled

The implementation includes checks for several important edge cases.

### Invalid authentication

Requests to protected endpoints without valid authentication are rejected.

### Invalid booking ID

Payment requests referencing a non-existent booking return an appropriate error.

### Unauthorized payment

A user cannot process payment for another user's booking.

### Invalid diagnostic test or centre

Booking creation validates that the referenced test and diagnostic centre exist.

The booking also verifies that the selected diagnostic test belongs to the selected centre.

### Invalid webhook status

Only:

```text
SUCCESS
FAILED
```

are accepted by the payment webhook.

### Repeated webhook events

Previously processed webhook event IDs are detected and are not processed again.

---

# Important Assumptions

The following assumptions were made for this assignment:

1. The payment service is simulated and does not connect to a real payment gateway.

2. Authentication uses JWT access tokens.

3. Diagnostic test prices are stored in the database and the booking amount is derived from the selected test price.

4. A diagnostic test belongs to one diagnostic centre.

5. A booking belongs to one user, one diagnostic test, and one diagnostic centre.

6. Webhook `event_id` values are treated as unique identifiers for payment events.

7. The application is intended as an assignment/demo backend and is not configured for production deployment.

8. PostgreSQL is used as the database as preferred in the assignment.

---

# Security Considerations

For the assignment:

- Passwords are stored as bcrypt hashes rather than plain text.
- Protected endpoints require JWT authentication.
- Users can only process payments for their own bookings.
- JWT-protected resources validate the token before accessing user-specific data.

For production, secrets such as the JWT secret key and database credentials should be stored in environment variables rather than source code.

---

# Future Improvements

If more development time were available, the following improvements could be added:

- Environment-based configuration for secrets and database credentials
- Alembic database migrations
- Docker and docker-compose
- Redis caching
- Celery/background jobs
- Structured application logging
- Pagination for listing APIs
- API rate limiting
- Webhook retry handling
- More granular booking state-transition validation
- More isolated test database/fixtures
- Expanded unit and integration test coverage
- Production-grade error handling and monitoring

---

# Conclusion

This project demonstrates a small backend system for diagnostic test bookings and simulated payments with:

- REST API design
- JWT authentication
- Relational database modelling
- SQLAlchemy ORM
- Booking and payment workflows
- Webhook processing
- Idempotency handling
- Authorization checks
- Automated API testing
- Swagger/OpenAPI documentation
