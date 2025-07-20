"""Analysis service for research gap detection"""

from typing import Dict, Any, List
from app.schema.models import AnalyzeRequest, TopicRequest
from app.service.llm_service import llm_service
from app.service.arxiv_service import fetch_papers_by_topic
from app.core.prompts import GAP_ANALYSIS_PROMPT, TOPIC_ANALYSIS_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def analyze_text(request: AnalyzeRequest) -> Dict[str, Any]:
    """Analyze a single text/abstract for research gaps"""
    logger.info(f"Analyzing text: {request.title}")
    
    # Prepare authors info
    authors_info = ""
    if request.authors:
        authors_info = f"Authors: {', '.join(request.authors)}"
    
    # Format prompt
    prompt = GAP_ANALYSIS_PROMPT.format(
        title=request.title,
        abstract=request.abstract,
        field=request.field.value,
        authors_info=authors_info
    )
    
    # Get analysis from LLM
    result = await llm_service.analyze_with_prompt(prompt)
    
    logger.info("Text analysis completed")
    return result


async def analyze_topic(request: TopicRequest) -> Dict[str, Any]:
    """Analyze multiple papers for a given topic"""
    logger.info(f"Analyzing topic: {request.topic}")
    
    # Fetch papers from arXiv
    papers = await fetch_papers_by_topic(
        request.topic,
        max_results=request.max_papers
    )
    
    if not papers:
        logger.warning(f"No papers found for topic: {request.topic}")
        return {
            "topic": request.topic,
            "papers_analyzed": 0,
            "common_gaps": [],
            "individual_results": [],
            "suggested_research_directions": [
                "No papers found for this topic. Try refining your search terms."
            ]
        }
    
    # Format papers info for prompt
    papers_info = ""
    for i, paper in enumerate(papers, 1):
        papers_info += f"""
Paper {i}:
Title: {paper.get('title', 'Unknown')}
Authors: {', '.join(paper.get('authors', ['Unknown']))}
Abstract: {paper.get('abstract', 'No abstract available')[:1000]}...
"""
    
    # Format prompt
    prompt = TOPIC_ANALYSIS_PROMPT.format(
        topic=request.topic,
        field=request.field.value,
        papers_info=papers_info
    )
    
    # Get analysis from LLM
    result = await llm_service.analyze_with_prompt(prompt)
    
    # Add metadata
    result["topic"] = request.topic
    result["papers_analyzed"] = len(papers)
    
    # Enrich individual results with paper metadata
    if "individual_results" in result:
        for i, individual_result in enumerate(result["individual_results"]):
            if i < len(papers):
                individual_result["authors"] = papers[i].get("authors")
                individual_result["abstract"] = papers[i].get("abstract", "")[:500]
                individual_result["url"] = papers[i].get("url")
    
    logger.info(f"Topic analysis completed for {len(papers)} papers")
    return result


async def validate_analysis_service() -> bool:
    """Validate that the analysis service is working"""
    try:
        # Test with a simple request
        test_request = AnalyzeRequest(
            title="Test Paper",
            abstract="This is a test abstract to validate the service.",
            field="general"
        )
        
        result = await analyze_text(test_request)
        return isinstance(result, dict) and "gaps" in result
        
    except Exception as e:
        logger.error(f"Analysis service validation failed: {str(e)}")
        return False
