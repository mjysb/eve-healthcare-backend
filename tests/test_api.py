import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
TEST_EMAIL = f"pytest_{uuid.uuid4().hex}@example.com"



def test_home():
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {
        "message": "EVE Healthcare Backend is running"
    }
def test_signup():
    response = client.post(
        "/signup",
        json={
            "name": "Test User",
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_login():
    response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_me_without_token():
    response = client.get("/me")

    assert response.status_code == 401

def test_me_with_token():
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert "user_id" in response.json()

def test_create_booking():
    # Login
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    # Create booking
    response = client.post(
        "/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "test_id": 1,
            "centre_id": 1,
            "appointment_datetime": "2026-10-01T10:00:00"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"

def test_payment():
    # Login
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    # Create a booking for this user
    booking_response = client.post(
        "/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "test_id": 1,
            "centre_id": 1,
            "appointment_datetime": "2026-10-02T10:00:00"
        }
    )

    assert booking_response.status_code == 200

    booking_id = booking_response.json()["booking_id"]

    # Make payment
    response = client.post(
        "/payments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "booking_id": booking_id
        }
    )

    assert response.status_code == 200
    assert response.json()["payment_status"] == "SUCCESS"
    assert response.json()["booking_status"] == "CONFIRMED"

def test_payment_invalid_booking():
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/payments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "booking_id": 999999
        }
    )

    assert response.status_code == 404

def test_payment_for_other_users_booking():
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/payments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "booking_id": 1
        }
    )

    assert response.status_code == 403

def test_webhook_idempotency():
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    # Create a fresh booking
    booking_response = client.post(
        "/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "test_id": 1,
            "centre_id": 1,
            "appointment_datetime": "2026-10-03T10:00:00"
        }
    )

    assert booking_response.status_code == 200

    booking_id = booking_response.json()["booking_id"]

    # First webhook
    webhook_data = {
        "event_id": "pytest-event-001",
        "booking_id": booking_id,
        "status": "SUCCESS"
    }

    first_response = client.post(
        "/payments/webhook",
        json=webhook_data
    )

    assert first_response.status_code == 200

    # Same webhook again
    second_response = client.post(
        "/payments/webhook",
        json=webhook_data
    )

    assert second_response.status_code == 200
    assert second_response.json()["message"] == "Webhook already processed"

def test_failed_payment_webhook():
    login_response = client.post(
        "/login",
        json={
            "email": TEST_EMAIL,
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    # Create a fresh booking
    booking_response = client.post(
        "/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "test_id": 1,
            "centre_id": 1,
            "appointment_datetime": "2026-10-04T10:00:00"
        }
    )

    assert booking_response.status_code == 200

    booking_id = booking_response.json()["booking_id"]

    # Send failed payment webhook
    response = client.post(
        "/payments/webhook",
        json={
            "event_id": f"pytest-failed-{uuid.uuid4().hex}",
            "booking_id": booking_id,
            "status": "FAILED"
        }
    )

    assert response.status_code == 200
    assert response.json()["booking_status"] == "FAILED"


def test_invalid_webhook_status():
    response = client.post(
    "/payments/webhook",
    json={
        "event_id": f"pytest-failed-{uuid.uuid4().hex}",
        "booking_id": 1,
        "status": "INVALID"
    }
    )

    assert response.status_code == 400

