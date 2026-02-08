import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test suite for getting activities"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_keys(self, client):
        """Test that activities have expected keys"""
        response = client.get("/activities")
        activities = response.json()
        
        assert len(activities) > 0
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignup:
    """Test suite for signing up for activities"""

    def test_signup_with_valid_email_and_activity(self, client):
        """Test successful signup"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup adds participant to activity list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball%20Team/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball Team"]["participants"]

    def test_signup_with_nonexistent_activity_returns_404(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup returns 400"""
        email = "duplicate@mergington.edu"
        # First signup
        client.post(f"/activities/Drama%20Club/signup?email={email}")
        
        # Second signup with same email
        response = client.post(
            f"/activities/Drama%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregister:
    """Test suite for unregistering from activities"""

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        email = "unregister@mergington.edu"
        activity = "Tennis%20Club"
        
        # First, sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant is removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Tennis Club"]["participants"]

    def test_unregister_with_nonexistent_activity_returns_404(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_not_registered_returns_400(self, client):
        """Test unregister when not registered returns 400"""
        response = client.post(
            "/activities/Art%20Studio/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_response_message(self, client):
        """Test unregister returns correct message"""
        email = "unregister2@mergington.edu"
        activity = "Robotics%20Club"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]


class TestRootRedirect:
    """Test suite for root endpoint"""

    def test_root_redirects_to_static_html(self, client):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
