"""Test configuration and fixtures"""

import pytest
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.api.app import create_app
from app.core.config import Settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    return Settings(
        app_name="AI Gap Finder Test",
        version="1.0.0-test",
        host="127.0.0.1",
        port=8001,
        debug=True,
        log_level="DEBUG",
        openai_api_key="test-key",
        openai_model="gpt-3.5-turbo",
        openai_temperature=0.7,
        openai_max_tokens=1000,
        openai_timeout=30,
        pdf_max_file_size=1048576,  # 1MB for testing
        pdf_allowed_extensions=[".pdf"],
        embedding_model="text-embedding-ada-002",
        embedding_chunk_size=500,
        embedding_chunk_overlap=100,
        arxiv_base_url="http://export.arxiv.org/api/query",
        arxiv_max_results=5
    )


@pytest.fixture
def client(mock_settings):
    """Create test client with mocked settings"""
    with patch('app.core.config.get_settings', return_value=mock_settings):
        app = create_app()
        return TestClient(app)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    mock_service = Mock()
    mock_service.analyze_with_prompt.return_value = {
        "key_findings": ["Test finding 1", "Test finding 2"],
        "gaps": [
            {
                "gap_description": "Test gap description",
                "confidence_score": 0.8,
                "gap_type": "methodological",
                "potential_impact": "High impact test"
            }
        ],
        "limitations": ["Test limitation 1"],
        "methodology_gaps": ["Test methodology gap"],
        "suggested_hypotheses": [
            {
                "hypothesis": "Test hypothesis",
                "rationale": "Test rationale",
                "feasibility_score": 0.7,
                "required_methods": ["Test method 1", "Test method 2"]
            }
        ],
        "future_directions": ["Test direction 1", "Test direction 2"]
    }
    return mock_service


@pytest.fixture
def mock_arxiv_service():
    """Mock arXiv service for testing"""
    mock_service = Mock()
    mock_service.search_papers.return_value = [
        {
            "title": "Test Paper 1",
            "abstract": "This is a test abstract for paper 1",
            "authors": ["Author 1", "Author 2"],
            "url": "http://arxiv.org/abs/test1",
            "published": "2023-01-01",
            "categories": ["cs.AI"]
        },
        {
            "title": "Test Paper 2", 
            "abstract": "This is a test abstract for paper 2",
            "authors": ["Author 3", "Author 4"],
            "url": "http://arxiv.org/abs/test2",
            "published": "2023-01-02",
            "categories": ["cs.LG"]
        }
    ]
    return mock_service


@pytest.fixture
def sample_analyze_request():
    """Sample request for analyze endpoint"""
    return {
        "title": "Test Research Paper",
        "abstract": "This is a test abstract for analyzing research gaps and limitations.",
        "field": "computer_science",
        "authors": ["Dr. Test Author"],
        "keywords": ["test", "research", "gaps"]
    }


@pytest.fixture
def sample_topic_request():
    """Sample request for topic endpoint"""
    return {
        "topic": "machine learning",
        "field": "computer_science",
        "max_papers": 5
    }


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing PDF extraction"""
    # This is a minimal PDF structure for testing
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""


# Environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    yield
    # Cleanup if needed
