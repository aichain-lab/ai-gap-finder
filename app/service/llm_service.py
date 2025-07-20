"""LLM service for OpenAI integration"""

import json
import asyncio
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.settings = get_settings()
        self._client = None
    
    @property
    def client(self) -> ChatOpenAI:
        """Get or create OpenAI client"""
        if self._client is None:
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            
            self._client = ChatOpenAI(
                model=self.settings.openai_model,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens,
                timeout=self.settings.openai_timeout,
                api_key=self.settings.openai_api_key
            )
        return self._client
    
    async def analyze_with_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze text using LLM with given prompt"""
        try:
            logger.info(f"Sending request to {self.settings.openai_model}")
            
            # Create message
            message = HumanMessage(content=prompt)
            
            # Get response from LLM
            response = await asyncio.to_thread(self.client.invoke, [message])
            
            # Parse JSON response
            response_text = response.content.strip()
            logger.debug(f"Raw LLM response: {response_text[:500]}...")
            
            # Clean up response if needed (remove markdown code blocks)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            try:
                result = json.loads(response_text)
                logger.info("Successfully parsed LLM response")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                
                # Try to extract JSON from partial response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_part = response_text[start_idx:end_idx + 1]
                    try:
                        result = json.loads(json_part)
                        logger.info("Successfully extracted JSON from partial response")
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # Return fallback response
                return self._create_fallback_response()
                
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return self._create_fallback_response()
    
    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create a fallback response when LLM fails"""
        return {
            "key_findings": ["Analysis temporarily unavailable"],
            "gaps": [
                {
                    "gap_description": "Unable to analyze gaps at this time. Please try again later.",
                    "confidence_score": 0.0,
                    "gap_type": "system",
                    "potential_impact": "Service unavailable"
                }
            ],
            "limitations": ["Service temporarily unavailable"],
            "methodology_gaps": ["Analysis not available"],
            "suggested_hypotheses": [
                {
                    "hypothesis": "Service analysis will be available after system recovery",
                    "rationale": "Technical limitation",
                    "feasibility_score": 1.0,
                    "required_methods": ["System restart"]
                }
            ],
            "future_directions": ["Retry analysis when service is available"]
        }
    
    async def validate_api_key(self) -> bool:
        """Validate OpenAI API key"""
        try:
            test_prompt = "Say 'API key valid' if you can read this."
            message = HumanMessage(content=test_prompt)
            response = await asyncio.to_thread(self.client.invoke, [message])
            return "API key valid" in response.content
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False


# Global instance
llm_service = LLMService()
