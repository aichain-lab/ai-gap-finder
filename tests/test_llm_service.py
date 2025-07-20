"""Tests for LLM service"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from app.service.llm_service import LLMService
from langchain.schema import HumanMessage


class TestLLMService:
    """Test LLM service functionality"""
    
    @pytest.fixture
    def llm_service(self, mock_settings):
        """Create LLM service with mock settings"""
        with patch('app.service.llm_service.get_settings', return_value=mock_settings):
            return LLMService()
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps({
            "key_findings": ["Finding 1"],
            "gaps": [
                {
                    "gap_description": "Test gap",
                    "confidence_score": 0.8,
                    "gap_type": "methodological",
                    "potential_impact": "High"
                }
            ],
            "limitations": ["Limitation 1"],
            "methodology_gaps": ["Method gap 1"],
            "suggested_hypotheses": [
                {
                    "hypothesis": "Test hypothesis",
                    "rationale": "Test rationale",
                    "feasibility_score": 0.7,
                    "required_methods": ["Method 1"]
                }
            ],
            "future_directions": ["Direction 1"]
        })
        mock_client.invoke.return_value = mock_response
        return mock_client
    
    @patch('app.service.llm_service.ChatOpenAI')
    def test_client_creation(self, mock_chat_openai, llm_service, mock_settings):
        """Test OpenAI client creation"""
        # Access client property to trigger creation
        client = llm_service.client
        
        mock_chat_openai.assert_called_once_with(
            model=mock_settings.openai_model,
            temperature=mock_settings.openai_temperature,
            max_tokens=mock_settings.openai_max_tokens,
            timeout=mock_settings.openai_timeout,
            api_key=mock_settings.openai_api_key
        )
    
    def test_client_creation_no_api_key(self, mock_settings):
        """Test client creation fails without API key"""
        mock_settings.openai_api_key = None
        
        with patch('app.service.llm_service.get_settings', return_value=mock_settings):
            llm_service = LLMService()
            
            with pytest.raises(ValueError, match="OpenAI API key not found"):
                _ = llm_service.client
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_analyze_with_prompt_success(self, mock_to_thread, llm_service, mock_openai_client):
        """Test successful analysis with prompt"""
        llm_service._client = mock_openai_client
        mock_to_thread.return_value = mock_openai_client.invoke.return_value
        
        test_prompt = "Test prompt for analysis"
        result = await llm_service.analyze_with_prompt(test_prompt)
        
        assert isinstance(result, dict)
        assert "key_findings" in result
        assert "gaps" in result
        assert len(result["gaps"]) > 0
        
        # Verify the client was called with correct message
        mock_to_thread.assert_called_once()
        args = mock_to_thread.call_args[0]
        assert callable(args[0])  # The function to run in thread
        assert len(args[1]) == 1  # Message list
        assert isinstance(args[1][0], HumanMessage)
        assert args[1][0].content == test_prompt
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_analyze_with_prompt_json_cleanup(self, mock_to_thread, llm_service, mock_openai_client):
        """Test JSON response cleanup (removing markdown code blocks)"""
        # Mock response with markdown code blocks
        mock_response = Mock()
        mock_response.content = '```json\n{"test": "value"}\n```'
        mock_openai_client.invoke.return_value = mock_response
        mock_to_thread.return_value = mock_response
        
        llm_service._client = mock_openai_client
        
        result = await llm_service.analyze_with_prompt("test prompt")
        
        assert result == {"test": "value"}
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_analyze_with_prompt_invalid_json(self, mock_to_thread, llm_service, mock_openai_client):
        """Test handling of invalid JSON response"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_openai_client.invoke.return_value = mock_response
        mock_to_thread.return_value = mock_response
        
        llm_service._client = mock_openai_client
        
        result = await llm_service.analyze_with_prompt("test prompt")
        
        # Should return fallback response
        assert result["key_findings"] == ["Analysis temporarily unavailable"]
        assert len(result["gaps"]) == 1
        assert result["gaps"][0]["gap_type"] == "system"
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_analyze_with_prompt_partial_json(self, mock_to_thread, llm_service, mock_openai_client):
        """Test extraction of JSON from partial response"""
        # Mock response with partial JSON
        mock_response = Mock()
        mock_response.content = 'Some text before {"test": "value", "key": "data"} some text after'
        mock_openai_client.invoke.return_value = mock_response
        mock_to_thread.return_value = mock_response
        
        llm_service._client = mock_openai_client
        
        result = await llm_service.analyze_with_prompt("test prompt")
        
        assert result == {"test": "value", "key": "data"}
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_analyze_with_prompt_exception(self, mock_to_thread, llm_service):
        """Test handling of exceptions during analysis"""
        mock_to_thread.side_effect = Exception("API error")
        
        result = await llm_service.analyze_with_prompt("test prompt")
        
        # Should return fallback response
        assert result["key_findings"] == ["Analysis temporarily unavailable"]
        assert result["gaps"][0]["gap_type"] == "system"
    
    def test_create_fallback_response(self, llm_service):
        """Test fallback response structure"""
        fallback = llm_service._create_fallback_response()
        
        assert isinstance(fallback, dict)
        assert "key_findings" in fallback
        assert "gaps" in fallback
        assert "suggested_hypotheses" in fallback
        assert "limitations" in fallback
        assert "methodology_gaps" in fallback
        assert "future_directions" in fallback
        
        # Check gap structure
        assert len(fallback["gaps"]) == 1
        gap = fallback["gaps"][0]
        assert "gap_description" in gap
        assert "confidence_score" in gap
        assert "gap_type" in gap
        assert "potential_impact" in gap
        assert gap["confidence_score"] == 0.0
        assert gap["gap_type"] == "system"
        
        # Check hypothesis structure
        assert len(fallback["suggested_hypotheses"]) == 1
        hypothesis = fallback["suggested_hypotheses"][0]
        assert "hypothesis" in hypothesis
        assert "rationale" in hypothesis
        assert "feasibility_score" in hypothesis
        assert "required_methods" in hypothesis
        assert hypothesis["feasibility_score"] == 1.0
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_validate_api_key_success(self, mock_to_thread, llm_service, mock_openai_client):
        """Test API key validation success"""
        mock_response = Mock()
        mock_response.content = "API key valid - test response"
        mock_openai_client.invoke.return_value = mock_response
        mock_to_thread.return_value = mock_response
        
        llm_service._client = mock_openai_client
        
        is_valid = await llm_service.validate_api_key()
        
        assert is_valid is True
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_validate_api_key_failure(self, mock_to_thread, llm_service, mock_openai_client):
        """Test API key validation failure"""
        mock_response = Mock()
        mock_response.content = "Invalid response"
        mock_openai_client.invoke.return_value = mock_response
        mock_to_thread.return_value = mock_response
        
        llm_service._client = mock_openai_client
        
        is_valid = await llm_service.validate_api_key()
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_validate_api_key_exception(self, mock_to_thread, llm_service):
        """Test API key validation with exception"""
        mock_to_thread.side_effect = Exception("API error")
        
        is_valid = await llm_service.validate_api_key()
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_analyze_with_empty_prompt(self, llm_service, mock_openai_client):
        """Test analysis with empty prompt"""
        llm_service._client = mock_openai_client
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_response = Mock()
            mock_response.content = '{"error": "empty prompt"}'
            mock_to_thread.return_value = mock_response
            
            result = await llm_service.analyze_with_prompt("")
            
            # Should still attempt to process
            mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_with_very_long_prompt(self, llm_service, mock_openai_client):
        """Test analysis with very long prompt"""
        llm_service._client = mock_openai_client
        long_prompt = "A" * 10000  # Very long prompt
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_response = Mock()
            mock_response.content = '{"result": "processed"}'
            mock_to_thread.return_value = mock_response
            
            result = await llm_service.analyze_with_prompt(long_prompt)
            
            mock_to_thread.assert_called_once()
            # Verify the prompt was passed correctly
            args = mock_to_thread.call_args[0]
            assert args[1][0].content == long_prompt
