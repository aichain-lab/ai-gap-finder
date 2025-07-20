"""PDF text extraction service"""

import fitz  # PyMuPDF
import pdfplumber
from typing import Optional, Dict, Any
from io import BytesIO
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFExtractor:
    """Service for extracting text from PDF files"""
    
    def __init__(self):
        self.settings = get_settings()
        self.max_file_size = self.settings.pdf_max_file_size
    
    def extract_text_pymupdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text using PyMuPDF"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            text_content = ""
            metadata = {
                "pages": doc.page_count,
                "method": "pymupdf"
            }
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_content += page.get_text()
                text_content += "\n\n"  # Separate pages
            
            doc.close()
            
            return {
                "text": text_content.strip(),
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {str(e)}")
            return {
                "text": "",
                "metadata": {"error": str(e), "method": "pymupdf"},
                "success": False
            }
    
    def extract_text_pdfplumber(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text using pdfplumber"""
        try:
            text_content = ""
            page_count = 0
            
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text
                        text_content += "\n\n"  # Separate pages
            
            metadata = {
                "pages": page_count,
                "method": "pdfplumber"
            }
            
            return {
                "text": text_content.strip(),
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            return {
                "text": "",
                "metadata": {"error": str(e), "method": "pdfplumber"},
                "success": False
            }
    
    def extract_text(self, pdf_bytes: bytes, method: str = "auto") -> Dict[str, Any]:
        """Extract text from PDF using specified method"""
        
        # Check file size
        if len(pdf_bytes) > self.max_file_size:
            return {
                "text": "",
                "metadata": {"error": f"File size exceeds {self.max_file_size} bytes"},
                "success": False
            }
        
        if method == "pymupdf":
            return self.extract_text_pymupdf(pdf_bytes)
        elif method == "pdfplumber":
            return self.extract_text_pdfplumber(pdf_bytes)
        else:  # auto
            # Try PyMuPDF first, fallback to pdfplumber
            result = self.extract_text_pymupdf(pdf_bytes)
            if result["success"] and result["text"].strip():
                return result
            
            logger.info("PyMuPDF failed or returned empty text, trying pdfplumber")
            return self.extract_text_pdfplumber(pdf_bytes)
    
    def extract_metadata_only(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract only metadata from PDF"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            metadata = {
                "page_count": doc.page_count,
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
            
            doc.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {"error": str(e)}
    
    def validate_pdf(self, pdf_bytes: bytes) -> bool:
        """Validate if the bytes represent a valid PDF"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            is_valid = doc.page_count > 0
            doc.close()
            return is_valid
        except:
            return False


# Global instance
pdf_extractor = PDFExtractor()


def extract_text_from_pdf(
    pdf_bytes: bytes, 
    method: str = "auto"
) -> Dict[str, Any]:
    """Extract text from PDF (convenience function)"""
    return pdf_extractor.extract_text(pdf_bytes, method)
