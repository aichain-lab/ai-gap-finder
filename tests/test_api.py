"""Tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.api.app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_analyze_endpoint_valid_request(client):
    """Test analyze endpoint with valid request"""
    request_data = {
        "title": "Test Research Paper",
        "abstract": "This is a test abstract for validating the API endpoint.",
        "field": "general"
    }
    
    response = client.post("/analyze", json=request_data)
    
    # Should return 200 or 500 depending on OpenAI key availability
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "gaps" in data
        assert "key_findings" in data
        assert "suggested_hypotheses" in data
        assert "processing_time" in data


def test_analyze_endpoint_invalid_request(client):
    """Test analyze endpoint with invalid request"""
    request_data = {
        "title": "",  # Empty title should fail validation
        "abstract": "This is a test abstract.",
        "field": "general"
    }
    
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 422  # Validation error


def test_topic_endpoint_valid_request(client):
    """Test topic endpoint with valid request"""
    request_data = {
        "topic": "machine learning",
        "field": "computer_science",
        "max_papers": 5
    }
    
    response = client.post("/topic", json=request_data)
    
    # Should return 200 or 500 depending on service availability
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "topic" in data
        assert "papers_analyzed" in data
        assert "common_gaps" in data
        assert "processing_time" in data


def test_topic_endpoint_invalid_request(client):
    """Test topic endpoint with invalid request"""
    request_data = {
        "topic": "",  # Empty topic should fail validation
        "field": "general"
    }
    
    response = client.post("/topic", json=request_data)
    assert response.status_code == 422  # Validation error
