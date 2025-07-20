"""Comprehensive tests for API endpoints"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestAnalyzeEndpoint:
    """Test the /analyze endpoint"""
    
    @patch('app.service.analysis.analyze_text')
    def test_analyze_endpoint_success(self, mock_analyze, client, sample_analyze_request):
        """Test successful analysis request"""
        mock_analyze.return_value = {
            "key_findings": ["Finding 1", "Finding 2"],
            "gaps": [
                {
                    "gap_description": "Test gap",
                    "confidence_score": 0.8,
                    "gap_type": "methodological",
                    "potential_impact": "High"
                }
            ],
            "suggested_hypotheses": [
                {
                    "hypothesis": "Test hypothesis",
                    "rationale": "Test rationale", 
                    "feasibility_score": 0.7,
                    "required_methods": ["Method 1"]
                }
            ],
            "limitations": ["Limitation 1"],
            "methodology_gaps": ["Gap 1"],
            "future_directions": ["Direction 1"]
        }
        
        response = client.post("/analyze", json=sample_analyze_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "processing_time" in data
        assert "gaps" in data
        assert "key_findings" in data
        assert len(data["gaps"]) > 0
        
        # Verify mock was called
        mock_analyze.assert_called_once()
    
    def test_analyze_endpoint_invalid_empty_title(self, client):
        """Test analysis with empty title"""
        invalid_request = {
            "title": "",
            "abstract": "Valid abstract",
            "field": "general"
        }
        
        response = client.post("/analyze", json=invalid_request)
        assert response.status_code == 422
    
    def test_analyze_endpoint_invalid_empty_abstract(self, client):
        """Test analysis with empty abstract"""
        invalid_request = {
            "title": "Valid title",
            "abstract": "",
            "field": "general"
        }
        
        response = client.post("/analyze", json=invalid_request)
        assert response.status_code == 422
    
    def test_analyze_endpoint_invalid_field(self, client):
        """Test analysis with invalid field"""
        invalid_request = {
            "title": "Valid title",
            "abstract": "Valid abstract",
            "field": "invalid_field"
        }
        
        response = client.post("/analyze", json=invalid_request)
        assert response.status_code == 422
    
    def test_analyze_endpoint_missing_required_fields(self, client):
        """Test analysis with missing required fields"""
        invalid_request = {
            "title": "Valid title"
            # Missing abstract and field
        }
        
        response = client.post("/analyze", json=invalid_request)
        assert response.status_code == 422
    
    @patch('app.service.analysis.analyze_text')
    def test_analyze_endpoint_service_error(self, mock_analyze, client, sample_analyze_request):
        """Test handling of service errors"""
        mock_analyze.side_effect = Exception("Service error")
        
        response = client.post("/analyze", json=sample_analyze_request)
        assert response.status_code == 500


class TestTopicEndpoint:
    """Test the /topic endpoint"""
    
    @patch('app.service.analysis.analyze_topic')
    def test_topic_endpoint_success(self, mock_analyze_topic, client, sample_topic_request):
        """Test successful topic analysis"""
        mock_analyze_topic.return_value = {
            "topic": "machine learning",
            "papers_analyzed": 5,
            "common_gaps": [
                {
                    "gap_description": "Common gap",
                    "confidence_score": 0.9,
                    "gap_type": "systematic",
                    "potential_impact": "Field-wide"
                }
            ],
            "individual_results": [
                {
                    "paper_title": "Paper 1",
                    "authors": ["Author 1"],
                    "abstract": "Abstract 1",
                    "gaps": [],
                    "url": "http://arxiv.org/abs/test1"
                }
            ],
            "suggested_research_directions": ["Direction 1"]
        }
        
        response = client.post("/topic", json=sample_topic_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "processing_time" in data
        assert "topic" in data
        assert "papers_analyzed" in data
        assert data["topic"] == "machine learning"
        
        mock_analyze_topic.assert_called_once()
    
    def test_topic_endpoint_invalid_empty_topic(self, client):
        """Test topic analysis with empty topic"""
        invalid_request = {
            "topic": "",
            "field": "general"
        }
        
        response = client.post("/topic", json=invalid_request)
        assert response.status_code == 422
    
    def test_topic_endpoint_invalid_max_papers(self, client):
        """Test topic analysis with invalid max_papers"""
        invalid_request = {
            "topic": "valid topic",
            "field": "general",
            "max_papers": 0  # Should be >= 1
        }
        
        response = client.post("/topic", json=invalid_request)
        assert response.status_code == 422
    
    def test_topic_endpoint_max_papers_too_high(self, client):
        """Test topic analysis with max_papers too high"""
        invalid_request = {
            "topic": "valid topic",
            "field": "general",
            "max_papers": 100  # Should be <= 50
        }
        
        response = client.post("/topic", json=invalid_request)
        assert response.status_code == 422
    
    @patch('app.service.analysis.analyze_topic')
    def test_topic_endpoint_service_error(self, mock_analyze_topic, client, sample_topic_request):
        """Test handling of topic service errors"""
        mock_analyze_topic.side_effect = Exception("Topic service error")
        
        response = client.post("/topic", json=sample_topic_request)
        assert response.status_code == 500


class TestHealthEndpoint:
    """Test the /health endpoint"""
    
    def test_health_endpoint_success(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint_returns_version(self, client):
        """Test that health endpoint returns version info"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


class TestAPIErrorHandling:
    """Test API error handling"""
    
    def test_invalid_json_request(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/analyze", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_unsupported_content_type(self, client):
        """Test handling of unsupported content type"""
        response = client.post(
            "/analyze",
            data="some data",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 422
    
    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_wrong_http_method(self, client):
        """Test using wrong HTTP method"""
        response = client.get("/analyze")  # Should be POST
        assert response.status_code == 405


class TestRequestValidation:
    """Test request validation edge cases"""
    
    def test_analyze_with_optional_fields(self, client):
        """Test analyze endpoint with all optional fields"""
        request_with_optionals = {
            "title": "Test Title",
            "abstract": "Test abstract",
            "field": "biology",
            "authors": ["Author 1", "Author 2"],
            "keywords": ["keyword1", "keyword2"]
        }
        
        with patch('app.service.analysis.analyze_text') as mock_analyze:
            mock_analyze.return_value = {
                "key_findings": [],
                "gaps": [],
                "suggested_hypotheses": [],
                "limitations": [],
                "methodology_gaps": [],
                "future_directions": []
            }
            
            response = client.post("/analyze", json=request_with_optionals)
            assert response.status_code == 200
    
    def test_topic_with_default_max_papers(self, client):
        """Test topic endpoint with default max_papers"""
        minimal_request = {
            "topic": "test topic",
            "field": "general"
        }
        
        with patch('app.service.analysis.analyze_topic') as mock_analyze:
            mock_analyze.return_value = {
                "topic": "test topic",
                "papers_analyzed": 0,
                "common_gaps": [],
                "individual_results": [],
                "suggested_research_directions": []
            }
            
            response = client.post("/topic", json=minimal_request)
            assert response.status_code == 200
    
    def test_very_long_title(self, client):
        """Test with very long title"""
        long_title = "A" * 1000  # Very long title
        request_data = {
            "title": long_title,
            "abstract": "Short abstract",
            "field": "general"
        }
        
        with patch('app.service.analysis.analyze_text') as mock_analyze:
            mock_analyze.return_value = {
                "key_findings": [],
                "gaps": [],
                "suggested_hypotheses": [],
                "limitations": [],
                "methodology_gaps": [],
                "future_directions": []
            }
            
            response = client.post("/analyze", json=request_data)
            # Should still work, just long
            assert response.status_code == 200
    
    def test_unicode_characters(self, client):
        """Test with unicode characters in request"""
        unicode_request = {
            "title": "测试标题 with émojis 🧠🔬",
            "abstract": "Test abstract with special chars: αβγδ",
            "field": "general"
        }
        
        with patch('app.service.analysis.analyze_text') as mock_analyze:
            mock_analyze.return_value = {
                "key_findings": [],
                "gaps": [],
                "suggested_hypotheses": [],
                "limitations": [],
                "methodology_gaps": [],
                "future_directions": []
            }
            
            response = client.post("/analyze", json=unicode_request)
            assert response.status_code == 200
