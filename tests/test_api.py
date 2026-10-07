from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()
    assert "Debate Team" in response.json()


def test_signup_for_activity_success(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Gym%20Class/signup?email=" + email)

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Gym Class"
    assert email in activities["Gym Class"]["participants"]


def test_signup_duplicate_student_returns_400(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup?email=" + email)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success(client):
    email = "daniel@mergington.edu"

    response = client.delete("/activities/Chess%20Club/unregister?email=" + email)

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    email = "missing@mergington.edu"

    response = client.delete("/activities/Chess%20Club/unregister?email=" + email)

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
