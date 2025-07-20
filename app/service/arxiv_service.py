"""arXiv service for fetching research papers"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ArXivService:
    """Service for fetching papers from arXiv"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.arxiv_base_url
    
    async def search_papers(
        self, 
        query: str, 
        max_results: int = 10,
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """Search for papers on arXiv"""
        try:
            # Encode query
            encoded_query = quote(query)
            url = f"{self.base_url}?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy={sort_by}"
            
            logger.info(f"Fetching papers from arXiv: {query}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"arXiv API returned status {response.status}")
                        return []
                    
                    xml_content = await response.text()
                    
            # Parse XML response
            papers = self._parse_arxiv_response(xml_content)
            logger.info(f"Found {len(papers)} papers for query: {query}")
            
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching papers from arXiv: {str(e)}")
            return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # Find all entry elements
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                paper = {}
                
                # Title
                title_elem = entry.find('atom:title', namespaces)
                if title_elem is not None:
                    paper['title'] = title_elem.text.strip().replace('\n', ' ')
                
                # Abstract
                summary_elem = entry.find('atom:summary', namespaces)
                if summary_elem is not None:
                    paper['abstract'] = summary_elem.text.strip().replace('\n', ' ')
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    name_elem = author.find('atom:name', namespaces)
                    if name_elem is not None:
                        authors.append(name_elem.text.strip())
                paper['authors'] = authors
                
                # URL
                id_elem = entry.find('atom:id', namespaces)
                if id_elem is not None:
                    paper['url'] = id_elem.text.strip()
                
                # Published date
                published_elem = entry.find('atom:published', namespaces)
                if published_elem is not None:
                    paper['published'] = published_elem.text.strip()
                
                # Categories
                categories = []
                for category in entry.findall('atom:category', namespaces):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                paper['categories'] = categories
                
                papers.append(paper)
                
        except ET.ParseError as e:
            logger.error(f"Error parsing arXiv XML response: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing arXiv response: {str(e)}")
        
        return papers
    
    async def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific paper by arXiv ID"""
        try:
            url = f"{self.base_url}?id_list={arxiv_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    xml_content = await response.text()
            
            papers = self._parse_arxiv_response(xml_content)
            return papers[0] if papers else None
            
        except Exception as e:
            logger.error(f"Error fetching paper {arxiv_id}: {str(e)}")
            return None


# Global instance
arxiv_service = ArXivService()


async def fetch_papers_by_topic(
    topic: str, 
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Fetch papers by topic (convenience function)"""
    return await arxiv_service.search_papers(topic, max_results)


async def fetch_recent_papers_by_field(
    field: str, 
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Fetch recent papers by research field"""
    
    # Map field names to arXiv categories
    field_mapping = {
        "computer_science": "cs.*",
        "physics": "physics.*",
        "mathematics": "math.*",
        "biology": "q-bio.*",
        "neuroscience": "q-bio.NC",
        "psychology": "q-bio.NC",
        "medicine": "q-bio.*",
        "chemistry": "physics.chem-ph",
        "general": ""
    }
    
    category = field_mapping.get(field, "")
    query = f"cat:{category}" if category else "all:*"
    
    return await arxiv_service.search_papers(
        query, 
        max_results=max_results,
        sort_by="lastUpdatedDate"
    )
