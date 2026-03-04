import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Test GET /activities
def test_get_activities():
    # Arrange
    # (No setup needed, uses in-memory data)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

# Test POST /activities/{activity_name}/signup
def test_signup_for_activity():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    # Cleanup
    client.delete(f"/activities/{activity}/unregister?email={email}")

# Test duplicate signup
def test_duplicate_signup():
    # Arrange
    activity = "Chess Club"
    email = "dupstudent@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    # Cleanup
    client.delete(f"/activities/{activity}/unregister?email={email}")

# Test unregister endpoint
def test_unregister_from_activity():
    # Arrange
    activity = "Chess Club"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"

# Test unregister for non-existent participant
def test_unregister_nonexistent():
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]

# Test signup for full activity
def test_signup_full_activity():
    # Arrange
    activity = "Chess Club"
    # Fill up the activity
    max_participants = client.get("/activities").json()[activity]["max_participants"]
    emails = [f"full{i}@mergington.edu" for i in range(max_participants)]
    for email in emails:
        client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    # Assert
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]
    # Cleanup
    for email in emails:
        client.delete(f"/activities/{activity}/unregister?email={email}")
