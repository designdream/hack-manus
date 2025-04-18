import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models.models import Base
from app.core.security import create_access_token
from app.schemas.schemas import UserCreate, User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Setup test database
Base.metadata.create_all(bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Test user data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "is_active": True,
    "is_superuser": False
}

# Test agent data
test_agent = {
    "name": "Test Agent",
    "description": "Test agent description",
    "status": "idle",
    "max_tasks": 5
}

# Test task data
test_task = {
    "title": "Test Task",
    "description": "Test task description",
    "status": "pending",
    "priority": 1,
    "progress": 0
}

# Helper function to create a test user
def create_test_user(db):
    from app.services.user_service import create_user
    user_in = UserCreate(**test_user)
    return create_user(db, user_in)

# Helper function to get authentication token
def get_auth_token(user_id):
    return create_access_token({"sub": str(user_id)})

# Test root endpoint
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome to Manus Manager API" in response.json()["message"]

# Test health check endpoint
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Test user authentication
def test_user_auth():
    # Create a test user
    db = TestingSessionLocal()
    user = create_test_user(db)
    db.close()
    
    # Test login
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Test get current user
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user["username"]
    assert response.json()["email"] == test_user["email"]
    
    # Test login with wrong password
    login_data = {
        "username": test_user["username"],
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401

# Test agent endpoints
def test_agent_crud():
    # Create a test user
    db = TestingSessionLocal()
    user = create_test_user(db)
    db.close()
    
    # Get auth token
    token = get_auth_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test create agent
    agent_data = {**test_agent, "owner_id": user.id}
    response = client.post("/agents", json=agent_data, headers=headers)
    assert response.status_code == 201
    created_agent = response.json()
    assert created_agent["name"] == test_agent["name"]
    assert created_agent["status"] == test_agent["status"]
    
    agent_id = created_agent["id"]
    
    # Test get all agents
    response = client.get("/agents", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == agent_id
    
    # Test get agent by id
    response = client.get(f"/agents/{agent_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == agent_id
    assert response.json()["name"] == test_agent["name"]
    
    # Test update agent
    update_data = {"name": "Updated Agent Name"}
    response = client.put(f"/agents/{agent_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Agent Name"
    
    # Test agent status operations
    response = client.post(f"/agents/{agent_id}/start", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    
    response = client.post(f"/agents/{agent_id}/pause", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "paused"
    
    response = client.post(f"/agents/{agent_id}/stop", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "idle"
    
    # Test delete agent
    response = client.delete(f"/agents/{agent_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify agent is deleted
    response = client.get(f"/agents/{agent_id}", headers=headers)
    assert response.status_code == 404

# Test task endpoints
def test_task_crud():
    # Create a test user
    db = TestingSessionLocal()
    user = create_test_user(db)
    db.close()
    
    # Get auth token
    token = get_auth_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test agent
    agent_data = {**test_agent, "owner_id": user.id}
    response = client.post("/agents", json=agent_data, headers=headers)
    agent_id = response.json()["id"]
    
    # Test create task
    task_data = {**test_task, "owner_id": user.id}
    response = client.post("/tasks", json=task_data, headers=headers)
    assert response.status_code == 201
    created_task = response.json()
    assert created_task["title"] == test_task["title"]
    assert created_task["status"] == test_task["status"]
    
    task_id = created_task["id"]
    
    # Test get all tasks
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == task_id
    
    # Test get task by id
    response = client.get(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == test_task["title"]
    
    # Test update task
    update_data = {"title": "Updated Task Title"}
    response = client.put(f"/tasks/{task_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task Title"
    
    # Test assign task to agent
    response = client.post(f"/tasks/{task_id}/assign/{agent_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["agent_id"] == agent_id
    
    # Test update task progress
    response = client.post(f"/tracking/tasks/{task_id}/progress/50", json={"task_status": "in_progress"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["progress"] == 50
    assert response.json()["status"] == "in_progress"
    
    # Test delete task
    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify task is deleted
    response = client.get(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 404
    
    # Clean up - delete agent
    client.delete(f"/agents/{agent_id}", headers=headers)

# Test analytics endpoints
def test_analytics():
    # Create a test user
    db = TestingSessionLocal()
    user = create_test_user(db)
    db.close()
    
    # Get auth token
    token = get_auth_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test data
    agent_data = {**test_agent, "owner_id": user.id}
    response = client.post("/agents", json=agent_data, headers=headers)
    agent_id = response.json()["id"]
    
    task_data = {**test_task, "owner_id": user.id}
    response = client.post("/tasks", json=task_data, headers=headers)
    task_id = response.json()["id"]
    
    # Test dashboard data
    response = client.get("/analytics/dashboard", headers=headers)
    assert response.status_code == 200
    dashboard = response.json()
    assert "agent_count" in dashboard
    assert "task_count" in dashboard
    assert dashboard["agent_count"] == 1
    assert dashboard["task_count"] == 1
    
    # Test agent stats
    response = client.get("/analytics/agents/stats", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # Test task stats
    response = client.get("/analytics/tasks/stats", headers=headers)
    assert response.status_code == 200
    assert "total_tasks" in response.json()
    assert response.json()["total_tasks"] == 1
    
    # Test agent performance
    response = client.get(f"/analytics/agents/{agent_id}/performance", headers=headers)
    assert response.status_code == 200
    assert "agent_id" in response.json()
    assert response.json()["agent_id"] == agent_id
    
    # Clean up
    client.delete(f"/tasks/{task_id}", headers=headers)
    client.delete(f"/agents/{agent_id}", headers=headers)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
