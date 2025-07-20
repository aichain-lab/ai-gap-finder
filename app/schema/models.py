"""Pydantic models for API requests and responses"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class FieldEnum(str, Enum):
    """Research field enumeration"""
    NEUROSCIENCE = "neuroscience"
    COMPUTER_SCIENCE = "computer_science"
    BIOLOGY = "biology"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    MEDICINE = "medicine"
    PSYCHOLOGY = "psychology"
    GENERAL = "general"


class AnalyzeRequest(BaseModel):
    """Request model for abstract/text analysis"""
    title: str = Field(..., description="Title of the research paper")
    abstract: str = Field(..., description="Abstract or text content to analyze")
    field: Optional[FieldEnum] = Field(
        FieldEnum.GENERAL, 
        description="Research field for context-specific analysis"
    )
    authors: Optional[List[str]] = Field(None, description="List of authors")
    keywords: Optional[List[str]] = Field(None, description="Keywords related to the research")
    
    @validator('abstract')
    def abstract_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Abstract cannot be empty')
        return v
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v


class TopicRequest(BaseModel):
    """Request model for topic-based gap analysis"""
    topic: str = Field(..., description="Research topic or keywords")
    field: Optional[FieldEnum] = Field(
        FieldEnum.GENERAL,
        description="Research field for context-specific analysis"
    )
    max_papers: Optional[int] = Field(
        10, 
        description="Maximum number of papers to analyze",
        ge=1,
        le=50
    )
    
    @validator('topic')
    def topic_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Topic cannot be empty')
        return v


class ResearchGap(BaseModel):
    """Individual research gap model"""
    gap_description: str = Field(..., description="Description of the identified gap")
    confidence_score: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)
    gap_type: str = Field(..., description="Type of gap (methodological, theoretical, empirical, etc.)")
    potential_impact: str = Field(..., description="Potential impact of addressing this gap")


class Hypothesis(BaseModel):
    """Research hypothesis model"""
    hypothesis: str = Field(..., description="Suggested research hypothesis")
    rationale: str = Field(..., description="Rationale behind the hypothesis")
    feasibility_score: float = Field(..., description="Feasibility score (0-1)", ge=0, le=1)
    required_methods: Optional[List[str]] = Field(None, description="Suggested research methods")


class AnalyzeResponse(BaseModel):
    """Response model for analysis results"""
    key_findings: List[str] = Field(..., description="Key findings from the research")
    gaps: List[ResearchGap] = Field(..., description="Identified research gaps")
    suggested_hypotheses: List[Hypothesis] = Field(..., description="Suggested research hypotheses")
    limitations: List[str] = Field(..., description="Identified limitations in the research")
    methodology_gaps: List[str] = Field(..., description="Gaps in methodology")
    future_directions: List[str] = Field(..., description="Suggested future research directions")
    processing_time: float = Field(..., description="Processing time in seconds")


class TopicAnalysisResult(BaseModel):
    """Individual topic analysis result"""
    paper_title: str = Field(..., description="Title of the analyzed paper")
    authors: Optional[List[str]] = Field(None, description="Authors of the paper")
    abstract: Optional[str] = Field(None, description="Abstract of the paper")
    gaps: List[ResearchGap] = Field(..., description="Identified gaps in this paper")
    url: Optional[str] = Field(None, description="URL to the paper")


class TopicResponse(BaseModel):
    """Response model for topic-based analysis"""
    topic: str = Field(..., description="Analyzed topic")
    papers_analyzed: int = Field(..., description="Number of papers analyzed")
    common_gaps: List[ResearchGap] = Field(..., description="Common gaps across papers")
    individual_results: List[TopicAnalysisResult] = Field(..., description="Results for individual papers")
    suggested_research_directions: List[str] = Field(..., description="Overall research directions")
    processing_time: float = Field(..., description="Processing time in seconds")


class EmbeddingRequest(BaseModel):
    """Request model for generating embeddings"""
    text: str = Field(..., description="Text to generate embeddings for")
    chunk_size: Optional[int] = Field(1000, description="Size of text chunks", ge=100, le=5000)


class EmbeddingResponse(BaseModel):
    """Response model for embeddings"""
    embeddings: List[List[float]] = Field(..., description="Generated embeddings")
    chunks: List[str] = Field(..., description="Text chunks")
    model_used: str = Field(..., description="Embedding model used")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
