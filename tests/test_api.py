"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that GET /activities contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Band",
            "Debate Team",
            "Robotics Club",
            "Chess Club",
            "Programming Class",
            "Gym Class",
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_adds_participant_to_activity(self):
        """Test that signup adds participant to activity"""
        email = "testuser123@mergington.edu"
        client.post(f"/activities/Basketball%20Team/signup?email={email}")
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball Team"]["participants"]

    def test_signup_duplicate_participant_returns_400(self):
        """Test that signing up duplicate participant returns 400"""
        email = "existing@mergington.edu"
        # Sign up first time
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        # Try to sign up again
        response = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_invalid_activity_returns_404(self):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_returns_success_message(self):
        """Test that signup returns success message"""
        email = "successtest@mergington.edu"
        response = client.post(f"/activities/Art%20Studio/signup?email={email}")
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]


class TestUnregister:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "unregistertest@mergington.edu"
        # Sign up first
        client.post(f"/activities/Music%20Band/signup?email={email}")
        # Unregister
        response = client.delete(f"/activities/Music%20Band/unregister?email={email}")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister removes participant from activity"""
        email = "removetest@mergington.edu"
        # Sign up
        client.post(f"/activities/Robotics%20Club/signup?email={email}")
        # Unregister
        client.delete(f"/activities/Robotics%20Club/unregister?email={email}")
        # Verify removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Robotics Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_non_participant_returns_400(self):
        """Test that unregistering non-participant returns 400"""
        response = client.delete(
            "/activities/Debate%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_returns_success_message(self):
        """Test that unregister returns success message"""
        email = "messagetestunreg@mergington.edu"
        # Sign up first
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        # Unregister
        response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]


class TestRootRedirect:
    """Test root endpoint redirect"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
