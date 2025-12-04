from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    # Backup activities state and provide a TestClient
    backup = deepcopy(activities)
    client = TestClient(app)
    yield client
    # Restore activities after test to avoid cross-test pollution
    activities.clear()
    activities.update(backup)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    test_email = "test.student@example.com"

    # Ensure test email is not already registered
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert test_email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Confirm it appears in participants
    resp = client.get("/activities")
    assert test_email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={test_email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Confirm removal
    resp = client.get("/activities")
    assert test_email not in resp.json()[activity]["participants"]


def test_signup_nonexistent_activity(client):
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert resp.status_code == 404


def test_double_signup(client):
    activity = "Chess Club"
    test_email = "dup@example.com"
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 400


def test_unregister_not_registered(client):
    activity = "Chess Club"
    resp = client.delete(f"/activities/{activity}/participants?email=not@there.com")
    assert resp.status_code == 400