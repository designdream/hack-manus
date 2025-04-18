import pytest
import os
import sys
import subprocess
import time
import requests
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.db.session import get_db, engine
from app.models.models import Base
from app.core.security import create_access_token
from app.schemas.schemas import UserCreate

# Test client
client = TestClient(app)

# Test user data
test_user = {
    "username": "integrationuser",
    "email": "integration@example.com",
    "password": "integrationpassword",
    "is_active": True,
    "is_superuser": False
}

# Test agent data
test_agent = {
    "name": "Integration Agent",
    "description": "Integration test agent",
    "status": "idle",
    "max_tasks": 5
}

# Test task data
test_task = {
    "title": "Integration Task",
    "description": "Integration test task",
    "status": "pending",
    "priority": 1,
    "progress": 0
}

# Backend process
backend_process = None

def setup_module(module):
    """Setup for the entire test module - start backend server"""
    global backend_process
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start backend server in a separate process
    backend_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    # Create test user
    db = next(get_db())
    from app.services.user_service import create_user
    user_in = UserCreate(**test_user)
    create_user(db, user_in)
    db.close()

def teardown_module(module):
    """Teardown for the entire test module - stop backend server"""
    global backend_process
    if backend_process:
        backend_process.terminate()
        backend_process.wait()

class TestIntegration:
    """Integration tests for the Manus Manager system"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Login to get auth token
        response = requests.post(
            "http://localhost:8000/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create test agent
        response = requests.post(
            "http://localhost:8000/agents",
            json={**test_agent, "owner_id": 1},
            headers=self.headers
        )
        assert response.status_code == 201
        self.agent_id = response.json()["id"]
        
        # Create test task
        response = requests.post(
            "http://localhost:8000/tasks",
            json={**test_task, "owner_id": 1},
            headers=self.headers
        )
        assert response.status_code == 201
        self.task_id = response.json()["id"]
    
    def teardown_method(self):
        """Teardown for each test method"""
        # Delete test task
        requests.delete(
            f"http://localhost:8000/tasks/{self.task_id}",
            headers=self.headers
        )
        
        # Delete test agent
        requests.delete(
            f"http://localhost:8000/agents/{self.agent_id}",
            headers=self.headers
        )
    
    def test_agent_task_workflow(self):
        """Test the complete agent-task workflow"""
        # Assign task to agent
        response = requests.post(
            f"http://localhost:8000/tasks/{self.task_id}/assign/{self.agent_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["agent_id"] == self.agent_id
        
        # Start agent
        response = requests.post(
            f"http://localhost:8000/agents/{self.agent_id}/start",
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "running"
        
        # Update task progress
        response = requests.post(
            f"http://localhost:8000/tracking/tasks/{self.task_id}/progress/25",
            json={"task_status": "in_progress"},
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["progress"] == 25
        assert response.json()["status"] == "in_progress"
        
        # Check dashboard data
        response = requests.get(
            "http://localhost:8000/analytics/dashboard",
            headers=self.headers
        )
        assert response.status_code == 200
        dashboard = response.json()
        assert dashboard["agent_count"] >= 1
        assert dashboard["task_count"] >= 1
        
        # Update task progress to complete
        response = requests.post(
            f"http://localhost:8000/tracking/tasks/{self.task_id}/progress/100",
            json={"task_status": "completed"},
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["progress"] == 100
        assert response.json()["status"] == "completed"
        
        # Stop agent
        response = requests.post(
            f"http://localhost:8000/agents/{self.agent_id}/stop",
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "idle"
        
        # Check agent performance
        response = requests.get(
            f"http://localhost:8000/analytics/agents/{self.agent_id}/performance",
            headers=self.headers
        )
        assert response.status_code == 200
        performance = response.json()
        assert performance["agent_id"] == self.agent_id
        assert performance["completed_tasks"] >= 1
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Test 404 for non-existent agent
        response = requests.get(
            "http://localhost:8000/agents/9999",
            headers=self.headers
        )
        assert response.status_code == 404
        
        # Test 404 for non-existent task
        response = requests.get(
            "http://localhost:8000/tasks/9999",
            headers=self.headers
        )
        assert response.status_code == 404
        
        # Test authentication error
        response = requests.get(
            "http://localhost:8000/agents",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        
        # Test validation error
        response = requests.post(
            "http://localhost:8000/agents",
            json={"invalid_field": "value"},
            headers=self.headers
        )
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
